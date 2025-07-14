from marshmallow import fields
from app.extensions import ma
from app.models import ServiceTickets
from app.models import Customer

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTickets
        include_fk = True

class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

edit_service_ticket_schema = EditServiceTicketSchema()
