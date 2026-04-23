from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json

from models.models import db, User, Analysis, SystemAnalytics
from routes.auth import auth_bp
from routes.user_dashboard import user_bp
from routes.admin_panel import admin_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fake_news.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extension init
db.init_app(app)
bcrypt = Bcrypt(app)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

# Landing Route
@app.route('/')
def index():
    return render_template('index.html')

# Database Initialization
with app.app_context():
    db.create_all()
    # Create Default Admin if none exists
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(
            name="System Administrator", 
            email="admin@fakenews.ai", 
            password=hashed_password, 
            phone="000-000-0000",
            role="admin"
        )
        db.session.add(admin_user)
        # Init System Analytics if none
        if not SystemAnalytics.query.first():
            db.session.add(SystemAnalytics())
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
