import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "super secret secrets" # This is the key to make sure its a token from your APR

def encode_token(id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),  # Token expires in 1 hour
        'iat': datetime.now(timezone.utc), # Issued at time
        'sub': str(id)  # Subject of the token, must be a string
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256') # This encodes the payload with the secret key using HS256 algorithm
    return token

def token_required(f):
    @wraps(f) # Whenever we wrap a function with token_required...we will call decorated and if it makes it through its checks, it will call
    # the wrapped function, which is f.
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split()[1].strip()
                print(f"Token received: {token}")  # Debugging log
            else:
                return jsonify({'message': 'Invalid Authorization header format. Expected "Bearer <token>".'}), 401

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                print(f"Decoded token data: {data}")  # Debugging log
                id = int(data['sub'])  # Convert back to integer

            except jwt.ExpiredSignatureError as error:
                print(f"Token expired: {error}")  # Debugging log
                return jsonify({'message': 'Token expired!'}), 400
            
            except jwt.InvalidTokenError as error:
                print(f"Invalid token error: {error}")  # Debugging log
                return jsonify({'message': 'Invalid token!'}), 400
            
            return f(id, *args, **kwargs)
        
        else:
            return jsonify({'message': 'You must be logged in to access this resource.'}), 401
        
    return decorated #Here it is called