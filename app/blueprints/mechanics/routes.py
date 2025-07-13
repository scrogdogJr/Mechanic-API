from flask import Flask, jsonify, request
from .schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select
from . import mechanics_bp

# CREATE MECHANIC
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({"error": "Mechanic with this email already exists"}), 400
    
    query = select(Mechanic).where(Mechanic.phone == mechanic_data['phone'])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({"error": "Mechanic with this phone number already exists"}), 400
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

# GET ALL MECHANICS
@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics)


# UPDATE MECHANIC
@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)
    
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# DELETE MECHANIC
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic.name} fired successfully"}), 200