from app.extensions import ma
from app.models import Customer, ServiceTickets

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(exclude=['name'])