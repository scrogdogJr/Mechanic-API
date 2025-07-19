from app import create_app
from app.models import db, Mechanic, ServiceTickets
from app.utils.util import encode_token
from datetime import date
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(name='John Doe', email='john.doe1@example.com', phone='123-456-7890', salary=50000)
        self.mechanic2 = Mechanic(name='John Doe2', email='john.doe2@example.com', phone='123-456-7891', salary=60000)
        self.service_ticket = ServiceTickets(service_date=date.today(), service_desc='Oil Change', VIN='fworiawrija', customer_id=1)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.add(self.mechanic2)
            db.session.add(self.service_ticket)
            db.session.commit()
            self.mechanic2.service_tickets.append(self.service_ticket)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            'name': 'John Doe3',
            'email': 'john.doe3@example.com',
            'phone': '123-456-7892',
            'salary': 70000
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe3')

    def test_get_all_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['email'], 'john.doe1@example.com')
        self.assertEqual(response.json[1]['email'], 'john.doe2@example.com')

    def test_update_mechanic(self):
        update_payload = {
            'name': 'John Doe Updated',
            'email': 'john.doe.updated@example.com',
            'phone': '123-456-7899',
            'salary': 55000
        }
        response = self.client.put(f'/mechanics/2', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John Doe Updated')
        self.assertEqual(response.json['email'], 'john.doe.updated@example.com')
        self.assertEqual(response.json['phone'], '123-456-7899')
        self.assertEqual(response.json['salary'], 55000)

    def test_delete_mechanic(self):
        response = self.client.delete('/mechanics/2')
        self.assertEqual(response.status_code, 204)

    def test_mechanic_experience(self):
        response = self.client.get('/mechanics/experience')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['name'], 'John Doe2')
        self.assertEqual(response.json[1]['name'], 'John Doe')

    def test_get_mechanic_by_name(self):
        response = self.client.get('/mechanics/search?name=John Doe2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['email'], 'john.doe2@example.com')
