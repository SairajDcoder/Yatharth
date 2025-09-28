from src.yatharth.database import db


class VerificationHistory(db.Model):
    __tablename__ = 'verification_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign key to link this record to a user
    user_email = db.Column(db.String(100), db.ForeignKey(
        'login.email'), nullable=False)

    # Details from the verified document
    student_name = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.String(50), nullable=False)
    certificate_id = db.Column(db.String(100), nullable=False)

    # Verification result
    # e.g., 'Verified', 'Fraud Detected'
    verification_status = db.Column(db.String(50), nullable=False)
    verified_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        """Helper function to convert model object to a dictionary."""
        return {
            'student_name': self.student_name,
            'institution': self.institution,
            'degree': self.degree,
            'verification_status': self.verification_status,
            # Format date for display
            'verified_at': self.verified_at.strftime('%B %d, %Y')
        }

    def __repr__(self):
        return f"<Verification for {self.student_name} [{self.verification_status}]>"
