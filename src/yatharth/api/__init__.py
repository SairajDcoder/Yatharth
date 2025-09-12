import os
from flask import request, Flask, render_template, redirect, url_for, jsonify, make_response
from flask_migrate import Migrate
from src.yatharth.api.endpoints import AUTH_BLUEPRINT
from src.yatharth.database import db
from src.yatharth.database.login_model import Login
from src.yatharth.database.verifyHistory_model import VerificationHistory
from src.yatharth.api.endpoints.login import MyForm


def create_app():
    app = Flask(__name__, template_folder="../templates",
                static_folder="../static")
    app.secret_key = "Syntax_Work"

    @app.route('/')
    def index():
        form = MyForm()
        return make_response(render_template("index.html", form=form, flag="False", username="Login"))

    @app.route('/admin')
    def admin():
        return render_template('admin/admin.html')

    psd = "sai3606"

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sai3606@localhost/YatharthDB'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sai3606@localhost:5432/YatharthDB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db, directory=os.path.join(
        "src", "yatharth", "alembic"))

    app.register_blueprint(AUTH_BLUEPRINT)

    return app
