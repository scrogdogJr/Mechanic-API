from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address) # get_remote_address is a function that returns the IP address of the client making the request...this ensures the limiter is applied per IP
cache = Cache()