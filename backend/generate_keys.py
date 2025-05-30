import secrets
import base64

# Generate secure random keys
jwt_secret = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
jwt_refresh_secret = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

print("Add these to your .env file:")
print(f"JWT_SECRET_KEY={jwt_secret}")
print(f"JWT_REFRESH_SECRET_KEY={jwt_refresh_secret}") 