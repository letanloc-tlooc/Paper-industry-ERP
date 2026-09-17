from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.user import User


db = SessionLocal()

try:
    user = db.scalar(
        select(User).where(
            User.username == "loc"
        )
    )

    if not user:
        print("User 'admin' not found.")

    else:
        print(f"User: {user.username}")

        print("\nRoles:")

        for role in user.roles:
            print(f"- {role.name}")

            print("  Permissions:")

            for permission in role.permissions:
                print(f"    - {permission.name}")

finally:
    db.close()