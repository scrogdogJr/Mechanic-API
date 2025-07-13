from flask import Blueprint

mechanics_bp = Blueprint('mechanics', __name__)  # This blueprint will handle mechanic-related routes

from . import routes