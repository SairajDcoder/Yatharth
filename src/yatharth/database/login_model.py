from src.yatharth.database import db


class Login(db.Model):
    __tablename__ = 'login'

    email = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"User with username {self.username} has logged in at {self.created_at}"
