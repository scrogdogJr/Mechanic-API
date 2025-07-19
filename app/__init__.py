from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp  # Assuming you have a mechanics blueprint defined similarly
from .blueprints.serviceTickets import service_tickets_bp  # Assuming you have a service tickets blueprint defined similarly
from .blueprints.inventory import inventory_bp  # Importing the inventory blueprint
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic DB"
    }
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}') # Allows us to pass in different configurations (i.e. databases)

    # Initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')  # Assuming customers_bp is defined in app/blueprints/customers/__init__.py
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')  # Assuming mechanics_bp is defined in app/blueprints/mechanics/__init__.py
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')  # Assuming service_tickets_bp is defined in app/blueprints/serviceTickets/__init__.py
    app.register_blueprint(inventory_bp, url_prefix='/inventory')  # Registering the inventory blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL) #Registering our swagger blueprint

    return app
