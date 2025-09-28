import os
from flask import request, Flask, render_template, redirect, url_for, jsonify, make_response, session
from flask_migrate import Migrate
from src.yatharth.api.endpoints import AUTH_BLUEPRINT
from src.yatharth.database import db
from src.yatharth.database.admin import AdminLogin
from src.yatharth.database.login_model import Login
from src.yatharth.database.verifyHistory_model import VerificationHistory

# MODIFIED: Import all form classes needed for the modal
from src.yatharth.api.endpoints.login import LoginForm, SignUpForm, ForgotPasswordForm


def create_app():
    app = Flask(__name__, template_folder="../templates",
                static_folder="../static")
    app.secret_key = "Syntax_Work"

    # --- ADD THESE TWO LINES ---
    # This tells Flask where to save uploaded files.
    app.config["UPLOAD_FOLDER"] = "uploads"
    # This creates the 'uploads' directory if it doesn't already exist.
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    # ---------------------------

    # MODIFIED: The main route now initializes all forms for the single-page modal
    @app.route('/')
    def index():
        login_form = LoginForm()
        signup_form = SignUpForm()
        forgot_password_form = ForgotPasswordForm()

        is_authenticated = 'username' in session
        username = session.get('username', 'Login')

        return make_response(render_template(
            "index.html",
            login_form=login_form,
            signup_form=signup_form,
            forgot_password_form=forgot_password_form,
            is_authenticated=is_authenticated,
            username=username
        ))

    @app.route('/admin')
    def admin():
        return render_template('Admin.html')

    psd = "sai3606"

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sai3606@localhost:5432/YatharthDB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db, directory=os.path.join(
        "src", "yatharth", "alembic"))

    app.register_blueprint(AUTH_BLUEPRINT)

    return app
