from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file, jsonify
from flask_login import login_required, current_user
from models.models import db, Analysis, User, SystemAnalytics, SpreadNode
from services.groq_service import GroqService
from services.pdf_service import PDFService
from services.location_service import get_location_from_ip
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

user_bp = Blueprint('user', __name__)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mkv', 'avi'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_bp.route('/dashboard')
@login_required
def dashboard():
    history = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.timestamp.desc()).limit(10).all()
    return render_template('user/dashboard.html', user=current_user, history=history)


@user_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    input_type = request.form.get('input_type')
    content = ""
    file_path = ""

    if input_type == 'url':
        content = request.form.get('url')
        if not content:
            flash("URL cannot be empty", "error")
            return redirect(url_for('user.dashboard'))
    else:
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            content = filename
        else:
            flash("Invalid file type or no file uploaded", "error")
            return redirect(url_for('user.dashboard'))

    analysis_data = GroqService().analyze_news(input_type, content if input_type == 'url' else file_path)

    if analysis_data.get('result') == "ERROR":
        flash(f"Analysis failed: {analysis_data.get('explanation')}", "error")
        return redirect(url_for('user.dashboard'))

    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in str(user_ip):
        user_ip = user_ip.split(',')[0].strip()

    location = get_location_from_ip(user_ip)

    new_analysis = Analysis(
        user_id=current_user.id,
        input_type=input_type,
        input_content=content,
        result=analysis_data['result'],
        confidence=analysis_data['confidence'],
        virality=analysis_data['virality'],
        explanation=analysis_data['explanation'],
        country=location['country'],
        country_code=location['country_code'],
        city=location['city'],
        latitude=location['latitude'],
        longitude=location['longitude']
    )
    db.session.add(new_analysis)
    db.session.flush()  # get new_analysis.id before commit

    # Generate & save geographic spread nodes
    try:
        from services.groq_service import GroqService as GS
        raw_nodes = GS().extract_spread_nodes(
            content=content,
            input_type=input_type,
            analysis_result=analysis_data['result'],
            explanation=analysis_data['explanation']
        )
        for node in raw_nodes:
            db.session.add(SpreadNode(
                analysis_id=new_analysis.id,
                location=node.get('location', 'Unknown'),
                latitude=float(node.get('latitude', 0)),
                longitude=float(node.get('longitude', 0)),
                intensity=float(node.get('intensity', 50)),
                platform=node.get('platform', 'Unknown'),
                detected_at=datetime.utcnow()
            ))
    except Exception as e:
        print(f"[SpreadNodes] Error generating nodes: {e}")

    analytics = SystemAnalytics.query.first()
    if not analytics:
        analytics = SystemAnalytics(total_analyses=0, fake_count=0, real_count=0, api_usage=0)
        db.session.add(analytics)

    analytics.total_analyses += 1
    if analysis_data['result'] == 'FAKE':
        analytics.fake_count += 1
    else:
        analytics.real_count += 1
    analytics.api_usage += 1

    db.session.commit()

    return render_template('user/result.html', data=new_analysis)


@user_bp.route('/download-report/<int:analysis_id>')
@login_required
def download_report(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    if analysis.user_id != current_user.id and current_user.role != 'admin':
        return "Unauthorized", 403

    report_filename = f"report_{analysis_id}_{uuid.uuid4()}.pdf"
    report_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report_filename)

    analysis_dict = {
        'result':        analysis.result,
        'confidence':    analysis.confidence,
        'virality':      analysis.virality,
        'input_type':    analysis.input_type,
        'input_content': analysis.input_content,
        'explanation':   analysis.explanation
    }

    PDFService.generate_report(analysis_dict, current_user.name, report_path)
    return send_file(report_path, as_attachment=True)


@user_bp.route('/history')
@login_required
def history():
    search = request.args.get('search', '')
    query = Analysis.query.filter_by(user_id=current_user.id)
    if search:
        query = query.filter(
            Analysis.explanation.like(f"%{search}%") |
            Analysis.input_content.like(f"%{search}%")
        )
    history_list = query.order_by(Analysis.timestamp.desc()).all()
    return render_template('user/history.html', history=history_list)

@user_bp.route('/heatmap')
@login_required
def heatmap():
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.timestamp.desc()).all()
    return render_template('user/heatmap.html', analyses=analyses, user=current_user)





@user_bp.route('/api/spread-nodes/<int:analysis_id>')
@login_required
def spread_nodes_api(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    if analysis.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({
        'analysis_id': analysis_id,
        'result':      analysis.result,
        'virality':    analysis.virality,
        'nodes':       [n.to_dict() for n in analysis.spread_nodes]
    })


@user_bp.route('/api/all-spread-nodes')
@login_required
def all_spread_nodes_api():
    analyses = Analysis.query.filter_by(user_id=current_user.id, result='FAKE').all()
    all_nodes = []
    for a in analyses:
        for n in a.spread_nodes:
            d = n.to_dict()
            d['analysis_content'] = a.input_content
            d['analysis_virality'] = a.virality
            all_nodes.append(d)
    return jsonify({'nodes': all_nodes, 'total': len(all_nodes)})