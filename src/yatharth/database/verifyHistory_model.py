from src.yatharth.database import db
from datetime import datetime


class VerificationHistory(db.Model):
    __tablename__ = 'verification_history'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), db.ForeignKey(
        'login.email'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional: Define a relationship to the Login model for easier access
    user = db.relationship('Login', backref='verifications')

    def __repr__(self):
        return f"Verification for {self.name} at {self.institution}, status: {self.status}"
