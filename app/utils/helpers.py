def hash_password(password):
  # Function to hash a password using a secure hashing algorithm
  import bcrypt
  hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
  return hashed

def check_password(hashed_password, user_password):
  # Function to check if the provided password matches the hashed password
  return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

def generate_token(user_id):
  # Function to generate a secure token for user sessions
  import jwt
  from datetime import datetime, timedelta
  secret_key = 'your_secret_key'  # Replace with your actual secret key
  expiration = datetime.utcnow() + timedelta(days=1)
  token = jwt.encode({'user_id': user_id, 'exp': expiration}, secret_key, algorithm='HS256')
  return token

def decode_token(token):
  # Function to decode a token and retrieve the user ID
  import jwt
  secret_key = 'your_secret_key'  # Replace with your actual secret key
  try:
    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    return payload['user_id']
  except jwt.ExpiredSignatureError:
    return None
  except jwt.InvalidTokenError:
    return None