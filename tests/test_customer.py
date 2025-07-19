from app import create_app
from app.models import db, Customer, ServiceTickets
from app.utils.util import encode_token
from datetime import date
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(name='John Doe', email='john.doe1@example.com', password='password')
        self.customer2 = Customer(name='John Doe2', email='john.doe2@example.com', password='password')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.add(self.customer2)
            db.session.commit()

        self.token = encode_token(1)
        self.customers = [self.customer, self.customer2]  # This is to test get all customers
        self.client = self.app.test_client()
            # Optionally, you can add test data here

    def test_create_customer(self):
        customer_payload = {
            'name': 'John Doe3',
            'email': 'john.doe3@example.com',
            'password': 'password'
        }
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe3')

    def test_invalid_creation(self):
        customer_payload = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['password'], ['Missing data for required field.'])

    def test_login_customer(self):
        login_payload = {
            'email': 'john.doe1@example.com',
            'password': 'password'
        }
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']
    
    def test_invalid_login(self):
        login_payload = {
            'email': 'john.doe1@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['Error'], 'Invalid email or password')

    def test_update_customer(self):
        update_payload = {
            'name': 'John Smith',
            'email': 'john.smith@example.com',
            'password': 'newpassword'
        }

        headers = {'Authorization': f'Bearer {self.test_login_customer()}'}

        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John Smith')
        self.assertEqual(response.json['email'], 'john.smith@example.com')
        self.assertEqual(response.json['password'], 'newpassword')

    def test_get_all_customers(self):
        
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['name'], 'John Doe')
        self.assertEqual(response.json[1]['name'], 'John Doe2')  # Assuming the second customer was created in test_create_customer

    def test_get_customer_by_id(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'John Doe')

    def test_delete_customer(self):
        headers = {'Authorization': f'Bearer {self.test_login_customer()}'}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_get_customer_tickets(self):
        headers = {'Authorization': f'Bearer {self.test_login_customer()}'}
        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'You have no service tickets!')
