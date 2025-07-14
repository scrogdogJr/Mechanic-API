from flask import Flask, jsonify, request
from .schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select
from . import mechanics_bp
from app.extensions import limiter, cache

# CREATE MECHANIC
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("10 per day")  # This is important to limit sp that if anyone gets into the admin side of the system, they can't make an overwhelming amount of mechanic employees. I can't imagine a shop would hire more than 10 per day.
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

    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page')) # Multiple args are separated by & in URL

        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics), 200
    except:
        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(mechanics), 200


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
@limiter.limit("10 per day")  # Limit to 10 requests per day
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {mechanic.name} fired successfully"}), 200

# SORT MECHANICS BY HOW MANY SERVICE TICKETS THEY HAVE
@mechanics_bp.route('/experience', methods=['GET'])
def get_mechanics_by_experience():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    

    return mechanics_schema.jsonify(mechanics)

# QUERY PARAMETERS: they appear after the ? in a URL, like /mechanics/search?name=John

# SEARCH MECHANICS BY NAME
@mechanics_bp.route('/search', methods=['GET'])
def search_mechanics():
    name = request.args.get('name')

    query = select(Mechanic).where(Mechanic.name.like(f'%{name}%'))

    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics)
