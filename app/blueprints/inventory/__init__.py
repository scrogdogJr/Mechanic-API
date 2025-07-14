from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__)  # This blueprint will handle inventory-related routes

from . import routes