from flask import jsonify, request
from .schemas import part_schema, parts_schema
from marshmallow import ValidationError
from app.models import Inventory, db
from sqlalchemy import select
from . import inventory_bp
from app.extensions import limiter, cache
from app.blueprints.serviceTickets.schemas import service_tickets_schema


# CREATE PART
@inventory_bp.route('/', methods=['POST'])
def create_part():

    try:
        part_data = part_schema.load(request.json)

    except ValidationError as error:
        return jsonify(error.messages), 400
    
    query = select(Inventory).where(Inventory.part_name == part_data['part_name'])
    part = db.session.execute(query).scalars().first()

    if part:
        return jsonify({"error": "Part with this name already exists"}), 400
    
    new_part = Inventory(**part_data)
    db.session.add(new_part)
    db.session.commit()
    return part_schema.jsonify(new_part), 201

# GET ALL PARTS
@inventory_bp.route('/', methods=['GET'])
def get_parts():

    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Inventory)
        parts = db.paginate(query, page=page, per_page=per_page)
        return parts_schema.jsonify(parts.items), 200
    except:

        query = select(Inventory)
        parts = db.session.execute(query).scalars().all()
        return parts_schema.jsonify(parts), 200
    
# GET PART BY ID
@inventory_bp.route('/<int:id>', methods=['GET'])
def get_part_by_id(id):

    query = select(Inventory).where(Inventory.part_id == id)
    part = db.session.execute(query).scalars().first()
    if not part:
        return jsonify({"error": "Part not found"}), 404
    return part_schema.jsonify(part), 200

# UPDATE PART
@inventory_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit('3 per hour')
def update_part(id):

    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    
    for key, value in part_data.items():
        setattr(part, key, value)

    db.session.commit()
    return part_schema.jsonify(part), 200

# DELETE PART
@inventory_bp.route('/<int:id>', methods=['DELETE'])
def delete_part(id):

    part = db.session.get(Inventory, id)

    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f'Part {part.part_name} deleted successfully!'}), 204
    
    