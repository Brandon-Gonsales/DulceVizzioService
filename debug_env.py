from dotenv import load_dotenv
import os

print("--- Debugging .env loading ---")
print(f"Current working directory: {os.getcwd()}")

# Intentar cargar .env explícitamente
env_path = os.path.join(os.getcwd(), '.env')
print(f"Checking for .env at: {env_path}")
if os.path.exists(env_path):
    print(".env file FOUND.")
else:
    print(".env file NOT FOUND.")

load_dotenv()

mongo_url = os.getenv("MONGODB_URL")
secret_key = os.getenv("SECRET_KEY")

print(f"MONGODB_URL loaded: {'YES' if mongo_url else 'NO'}")
print(f"SECRET_KEY loaded: {'YES' if secret_key else 'NO'}")

if mongo_url:
    print(f"MONGODB_URL value (first 20 chars): {mongo_url[:20]}...")
else:
    print("MONGODB_URL is None")

try:
    from app.config import settings
    print("Settings loaded successfully via Pydantic!")
except Exception as e:
    print(f"Pydantic Settings failed to load: {e}")
