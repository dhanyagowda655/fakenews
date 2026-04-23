from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black, green, red
import os

class PDFService:
    @staticmethod
    def generate_report(analysis_data, user_name, output_path):
        """
        analysis_data: { 
            'result': 'FAKE'|'REAL', 
            'confidence': 92.5, 
            'virality': 85.0, 
            'input_type': 'url', 
            'input_content': '...', 
            'explanation': '...' 
        }
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor("#1A1A2E"),
            alignment=1, # Center
            spaceAfter=30
        )
        
        result_color = green if analysis_data['result'] == 'REAL' else red
        result_style = ParagraphStyle(
            'ResultLabel',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=result_color,
            alignment=1,
            spaceAfter=20
        )
        
        content = []
        
        # Header
        content.append(Paragraph("AI-POWERED FAKE NEWS DETECTION REPORT", title_style))
        content.append(Spacer(1, 12))
        
        # User & Analysis Meta
        content.append(Paragraph(f"<b>User:</b> {user_name}", styles['Normal']))
        content.append(Paragraph(f"<b>Type:</b> {analysis_data['input_type'].upper()}", styles['Normal']))
        content.append(Paragraph(f"<b>Source/File:</b> {analysis_data['input_content']}", styles['Normal']))
        content.append(Spacer(1, 12))
        
        # Result & Scores
        content.append(Paragraph(f"ANALYSIS RESULT: {analysis_data['result']}", result_style))
        content.append(Paragraph(f"<b>Confidence Score:</b> {analysis_data['confidence']:.1f}%", styles['Normal']))
        content.append(Paragraph(f"<b>Virality Prediction:</b> {analysis_data['virality']:.1f}%", styles['Normal']))
        content.append(Spacer(1, 20))
        
        # AI Explanation
        content.append(Paragraph("<b>Detailed AI Explanation:</b>", styles['Heading3']))
        content.append(Paragraph(analysis_data['explanation'], styles['Normal']))
        
        # Build PDF
        doc.build(content)
        return output_path
