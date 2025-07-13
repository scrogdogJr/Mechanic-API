from flask import Blueprint

customers_bp = Blueprint('customers', __name__) # This blueprint will handle customer-related routes...behaves like a mini flask app

from . import routes  # Import routes to register them with the blueprint