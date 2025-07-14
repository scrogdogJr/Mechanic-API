from flask import Flask, jsonify, request
from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema
from marshmallow import ValidationError
from app.models import ServiceTickets, db, Mechanic, Inventory
from sqlalchemy import select
from . import service_tickets_bp
from app.extensions import cache
from app.utils.util import token_required

# CREATE SERVICE TICKET
@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():

    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400

    new_service_ticket = ServiceTickets(**service_ticket_data)
    db.session.add(new_service_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_service_ticket), 201

# ASSIGN MECHANIC TO SERVICE TICKET
@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic_to_ticket(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTickets, ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    if mechanic in ticket.mechanics:
        return jsonify({"error": "Mechanic already assigned to this ticket"}), 400
    
    ticket.mechanics.append(mechanic)
    db.session.commit()

    return jsonify({"message": f"Mechanic {mechanic.name} assigned to ticket {ticket.id} successfully"}), 200

# REMOVE MECHANIC FROM SERVICE TICKET
@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic_from_ticket(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTickets, ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic not assigned to this ticket"}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return jsonify({"message": f"Mechanic {mechanic.name} removed from ticket {ticket.id} successfully"}), 200

# GET ALL SERVICE TICKETS
@service_tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60) 
def get_all_service_tickets():
    query = select(ServiceTickets)

    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200


# UPDATE SERVICE TICKET
@service_tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
def update_service_ticket(ticket_id):

    try:
        service_ticket_data = edit_service_ticket_schema.load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400

    query = select(ServiceTickets).where(ServiceTickets.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()

    for mechanic_id in service_ticket_data['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in service_ticket_data['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

# ADD PART TO SERVICE TICKET
@service_tickets_bp.route('/<int:ticket_id>/add-part/<int:part_id>', methods=['PUT'])
def add_part_to_service_ticket(ticket_id, part_id):
    ticket = db.session.get(ServiceTickets, ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    part = db.session.get(Inventory, part_id)

    if not part:
        return jsonify({"error": "Part not found"}), 404
    
    if part in ticket.parts:
        return jsonify({"error": "Part already added to this ticket"}), 400
    
    ticket.parts.append(part)
    db.session.commit()

    return jsonify({"message": f"Part {part.part_name} added to ticket {ticket.id} successfully"}), 200
