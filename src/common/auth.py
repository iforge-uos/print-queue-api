from functools import wraps
from flask import request
from models.auth_keys import auth_model
from common.routing import custom_response
import secrets


def generate_hash_key():
    """
    Function to generate keys for the clients to use for the API \n
    Parameters:
        none:
    Returns:
        key: the hashkey
    """
    return secrets.token_urlsafe(64)


def verify_key_and_access_level(key, level):
   """
   Match API keys and discard ip
   @param key: API key from request
   @return: boolean
   """
   print(key)
   if key is None:
      return False
   api_key = auth_model.get_key_by_key(key)
   if api_key is None:
      return False
   # check the permission level of the key is higher than what is required for this resource 
   elif api_key.permission_value >= level:
      return True
   return False


def requires_access_level(access_level):
   def decorator(f):
      @wraps(f)
      def decorated_function(*args, **kwargs):
         key = request.headers.get("x-api-key")
         if key is None:
            return custom_response({"error" : "please supply api key in the request header"}, 400)
         if not verify_key_and_access_level(key, access_level):
            return custom_response({"error" : "you are not allowed to access this resource"}, 401)
         return f(*args, **kwargs)
      return decorated_function
   return decorator