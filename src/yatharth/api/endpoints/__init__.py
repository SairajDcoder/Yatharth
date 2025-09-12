from flask import Blueprint
from flask_restx import Api

from src.yatharth.api.endpoints.login import LOGIN_API
from src.yatharth.api.endpoints.contact import CONTACT_API
from src.yatharth.api.endpoints.verification import VERIFICATION_API

AUTH_BLUEPRINT = Blueprint('log', __name__)


API = Api(AUTH_BLUEPRINT)
API.add_namespace(LOGIN_API)
API.add_namespace(CONTACT_API)
API.add_namespace(VERIFICATION_API)
