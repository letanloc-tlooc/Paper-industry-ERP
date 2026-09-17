from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.user import User
from app.models.role import Role


db = SessionLocal()

try:
    user = db.scalar(
        select(User).where(
            User.username == "loc"
        )
    )

    role = db.scalar(
        select(Role).where(
            Role.name == "ADMIN"
        )
    )

    if user and role:

        if role not in user.roles:
            user.roles.append(role)

        db.commit()

        print("ADMIN role assigned.")

finally:
    db.close()