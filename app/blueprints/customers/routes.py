from flask import Flask, jsonify, request
from .schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from app.models import Customer
from sqlalchemy import select
from app.models import db, Customer
from . import customers_bp


#CREATE CUSTOMER
@customers_bp.route('/', methods=['POST'])
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
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all() # scalars() translates the db object into python readable format...all() returns a list

    return customers_schema.jsonify(customers), 200

#GET CUSTOMER BY ID
@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    customer = db.session.get(Customer, id)
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found"}), 400

#UPDATE CUSTOMER
@customers_bp.route('/<int:id>', methods=['PUT'])
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
@customers_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": f'Customer {customer.name} deleted successfully!'}), 200
    return jsonify({"error": "Customer not found"}), 400
