from app import create_app
from app.models import Inventory, db, Mechanic, ServiceTickets
import unittest

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.part = Inventory(part_id=1, part_name='Oil Filter', price=10.99)
        self.part2 = Inventory(part_id=2, part_name='Air Filter', price=15.99)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.part)
            db.session.add(self.part2)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_part(self):
        part_payload = {
            'part_name': 'Brake Pad',
            'price': 25.99
        }
        response = self.client.post('/inventory/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], 'Brake Pad')

    def test_get_all_parts(self):
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['part_name'], 'Oil Filter')
        self.assertEqual(response.json[1]['part_name'], 'Air Filter')

    def test_get_part_by_id(self):
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'Oil Filter')

    def test_delete_part(self):
        response = self.client.delete('/inventory/2')
        self.assertEqual(response.status_code, 204)

    def test_update_part(self):
        update_payload = {
            'part_name': 'Updated Oil Filter',
            'price': 12.99
        }
        response = self.client.put('/inventory/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'Updated Oil Filter')
        self.assertEqual(response.json['price'], 12.99)

