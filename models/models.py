from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='user') # user or admin
    analyses = db.relationship('Analysis', backref='user', lazy=True)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    input_type = db.Column(db.String(50), nullable=False) # url, image, video
    input_content = db.Column(db.String(500), nullable=False) # URL or Filename
    result = db.Column(db.String(10), nullable=False) # FAKE or REAL
    confidence = db.Column(db.Float, nullable=False)
    virality = db.Column(db.Float, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    country      = db.Column(db.String(100), default='Unknown')
    country_code = db.Column(db.String(10),  default='UN')
    city         = db.Column(db.String(100), default='Unknown')
    latitude     = db.Column(db.Float,       default=0.0)
    longitude    = db.Column(db.Float,       default=0.0)
    spread_nodes = db.relationship('SpreadNode', backref='analysis', lazy=True)
    
class SpreadNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    location = db.Column(db.String(200), default='Unknown')
    latitude = db.Column(db.Float, default=0.0)
    longitude = db.Column(db.Float, default=0.0)
    intensity = db.Column(db.Float, default=0.0)
    platform = db.Column(db.String(100), default='Unknown')
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'intensity': self.intensity,
            'platform': self.platform,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }
    
class SystemAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_analyses = db.Column(db.Integer, default=0)
    fake_count = db.Column(db.Integer, default=0)
    real_count = db.Column(db.Integer, default=0)
    api_usage = db.Column(db.Integer, default=0) # Token count or Request count
