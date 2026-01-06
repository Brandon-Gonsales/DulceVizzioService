import asyncio
import traceback
from app.database import connect_to_mongo
from app.services.auth_service import auth_service
from app.schemas.user_schema import UserCreate
from app.models.enums import Role

async def main():
    try:
        print("Connecting to DB...")
        await connect_to_mongo()
        print("Connected.")
        
        user_data = UserCreate(
            email="debug_internal@example.com",
            password="Password123",
            full_name="Debug Internal",
            username="debuginternal",
            role=Role.SUPERADMIN
        )
        
        print("Attempting register_user...")
        user = await auth_service.register_user(user_data, created_by=None)
        print(f"Success! User created: {user.email}")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
