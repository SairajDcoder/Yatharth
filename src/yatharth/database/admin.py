from src.yatharth.database import db


class AdminLogin(db.Model):
    __tablename__ = 'admin_login'

    email = db.Column(db.String(100), primary_key=True)
    # Increased length to 300 to safely store long password hashes
    password = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Admin User {self.email}>"
