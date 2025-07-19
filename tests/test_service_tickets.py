from app import create_app
from app.models import Inventory, db, Mechanic, ServiceTickets
from datetime import date
import unittest

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(name='John Doe', email='john.doe1@example.com', phone='123-456-7890', salary=50000)
        self.mechanic2 = Mechanic(name='John Doe2', email='john.doe2@example.com', phone='123-456-7891', salary=60000)
        self.service_ticket = ServiceTickets(service_date=date.today(), service_desc='Oil Change', VIN='fworiawrija', customer_id=1)
        self.service_ticket2 = ServiceTickets(service_date=date.today(), service_desc='Tire Rotation', VIN='1234567890', customer_id=1)
        self.part = Inventory(part_id=1, part_name='Oil Filter', price=10.99)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.add(self.mechanic2)
            db.session.add(self.service_ticket)
            db.session.add(self.service_ticket2)
            db.session.add(self.part)
            db.session.commit()
            self.mechanic2.service_tickets.append(self.service_ticket)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_service_ticket(self):
        service_ticket_payload = {
            'service_date': str(date.today()),
            'service_desc': 'Brake Inspection',
            'VIN': '1HGCM82633A123456',
            'customer_id': 1
        }
        response = self.client.post('/service-tickets/', json=service_ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['service_desc'], 'Brake Inspection')

    def test_assign_mechanic_to_ticket(self):
        response = self.client.put('/service-tickets/1/assign-mechanic/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Mechanic John Doe assigned to ticket 1 successfully')

    def test_remove_mechanic_from_ticket(self):
        response = self.client.put('/service-tickets/1/remove-mechanic/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Mechanic John Doe2 removed from ticket 1 successfully')

    def test_get_all_service_tickets(self):
        response = self.client.get('/service-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_update_service_ticket(self):
        update_payload = {
            'add_mechanic_ids': [2],
            'remove_mechanic_ids': [1],
        }
        response = self.client.put('/service-tickets/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_desc'], 'Oil Change')

    def test_add_part_to_ticket(self):
        response = self.client.put('/service-tickets/1/add-part/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Part Oil Filter added to ticket 1 successfully')