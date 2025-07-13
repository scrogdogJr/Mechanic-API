from flask import Flask
from .extensions import ma
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp  # Assuming you have a mechanics blueprint defined similarly
from .blueprints.serviceTickets import service_tickets_bp  # Assuming you have a service tickets blueprint defined similarly

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}') # Allows us to pass in different configurations (i.e. databases)

    # Initialize extensions
    ma.init_app(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')  # Assuming customers_bp is defined in app/blueprints/customers/__init__.py
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')  # Assuming mechanics_bp is defined in app/blueprints/mechanics/__init__.py
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')  # Assuming service_tickets_bp is defined in app/blueprints/serviceTickets/__init__.py
    # Setting up the URL prefix for the customers blueprint allows it to auto fill on routes

    return app
