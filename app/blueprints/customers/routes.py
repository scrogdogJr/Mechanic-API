from flask import Flask, jsonify, request
from .schemas import customer_schema, customers_schema, login_schema
from marshmallow import ValidationError
from app.models import Customer
from sqlalchemy import select
from app.models import db, Customer, ServiceTickets
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required
from app.blueprints.serviceTickets.schemas import service_tickets_schema

@customers_bp.route('/login', methods=['POST'])
def login():

    try:
        credentials = login_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    query = select(Customer).where(Customer.email == credentials['email'])
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == credentials['password']:
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Login successful",
            "token": token
        }

        return jsonify(response), 200
    
    else:
        return jsonify({"Error": "Invalid email or password"}), 401
    

#CREATE CUSTOMER
@customers_bp.route('/', methods=['POST'])
@limiter.limit("5 per day")  # Limit to 5 requests per day
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)

    except ValidationError as error:
        return jsonify(error.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    db.session.execute(query).scalars().all()
    existing_customer = db.session.execute(query).scalars().first()
    if existing_customer:
        return jsonify({"error": "Customer with this email already exists"}), 400
    new_customer = Customer(**customer_data) # ** will unpack the dictionary into keyword arguments
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201 # The schema is needed to serialize the object into JSON format


#GET ALL CUSTOMERS
@customers_bp.route('/', methods=['GET'])
# This cache is here because customers will probably be displayed on a page or searched for frequently. But, it is only 60 seconds just in case a newly created customer needs to be accessed quickly.
def get_customers():

    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page')) # Multiple args are separated by & in URL

        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page) # paginate returns a Pagination object that contains the items, total, pages, etc.
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all() # scalars() translates the db object into python readable format...all() returns a list

        return customers_schema.jsonify(customers), 200


#GET CUSTOMER BY ID
@customers_bp.route('/<int:id>', methods=['GET'])
@cache.cached(timeout=60)
def get_customer(id):
    customer = db.session.get(Customer, id)
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found"}), 400

#UPDATE CUSTOMER
@customers_bp.route('/', methods=['PUT'])
@limiter.limit("1 per month") 
@token_required   
def update_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#DELETE CUSTOMER
@customers_bp.route('/', methods=['DELETE'])
@limiter.limit("5 per day")  # Limit to 5 requests per day
@token_required # This has the customer_id in it, so it will be passed to the function
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": f'Customer {customer.name} deleted successfully!'}), 204
    return jsonify({"error": "Customer not found"}), 400

# GET CUSTOMER TICKETS
@customers_bp.route('/my-tickets', methods=['GET'])
@cache.cached(timeout=120)
@token_required
def get_customer_tickets(id):

    query = select(ServiceTickets).where(ServiceTickets.customer_id == id)

    service_tickets = db.session.execute(query).scalars().all()

    if not service_tickets:
        return jsonify({"message": "You have no service tickets!"}), 404

    return service_tickets_schema.jsonify(service_tickets), 200
