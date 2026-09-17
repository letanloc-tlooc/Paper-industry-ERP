from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.role import Role, Permission


PERMISSIONS = [
    ("user:read", "View users"),
    ("user:create", "Create users"),
    ("user:update", "Update users"),
    ("user:delete", "Delete users"),

    ("product:read", "View products"),
    ("product:create", "Create products"),
    ("product:update", "Update products"),
    ("product:delete", "Delete products"),

    ("inventory:read", "View inventory"),
    ("inventory:write", "Modify inventory"),

    ("purchase:read", "View purchases"),
    ("purchase:create", "Create purchases"),
    ("purchase:update", "Update purchases"),

    ("sales:read", "View sales"),
    ("sales:create", "Create sales"),
    ("sales:update", "Update sales"),

    ("production:read", "View production"),
    ("production:create", "Create production"),
    ("production:update", "Update production"),

    ("qc:read", "View quality inspections"),
    ("qc:create", "Create quality inspections"),
    ("qc:update", "Update quality inspections"),

    ("report:read", "View reports"),
]


ROLES = [
    ("ADMIN", "System administrator"),
    ("WAREHOUSE", "Warehouse staff"),
    ("PURCHASING", "Purchasing staff"),
    ("SALES", "Sales staff"),
    ("PRODUCTION", "Production staff"),
    ("QC", "Quality control staff"),
    ("ACCOUNTANT", "Accountant"),
]


role_permissions_map = {
    "ADMIN": [
        "user:read",
        "user:create",
        "user:update",
        "user:delete",

        "product:read",
        "product:create",
        "product:update",
        "product:delete",

        "inventory:read",
        "inventory:write",

        "purchase:read",
        "purchase:create",
        "purchase:update",

        "sales:read",
        "sales:create",
        "sales:update",

        "production:read",
        "production:create",
        "production:update",

        "qc:read",
        "qc:create",
        "qc:update",

        "report:read",
    ],

    "WAREHOUSE": [
        "product:read",
        "inventory:read",
        "inventory:write",
        "purchase:read",
        "sales:read",
        "report:read",
    ],

    "PURCHASING": [
        "product:read",
        "purchase:read",
        "purchase:create",
        "purchase:update",
        "inventory:read",
    ],

    "SALES": [
        "product:read",
        "inventory:read",
        "sales:read",
        "sales:create",
        "sales:update",
        "report:read",
    ],

    "PRODUCTION": [
        "product:read",
        "inventory:read",
        "production:read",
        "production:create",
        "production:update",
    ],

    "QC": [
        "production:read",
        "qc:read",
        "qc:create",
        "qc:update",
    ],

    "ACCOUNTANT": [
        "purchase:read",
        "sales:read",
        "inventory:read",
        "report:read",
    ],
}


def seed():
    db = SessionLocal()

    try:
        # 1. Create permissions
        for name, description in PERMISSIONS:
            permission = db.scalar(
                select(Permission).where(
                    Permission.name == name
                )
            )

            if not permission:
                permission = Permission(
                    name=name,
                    description=description
                )
                db.add(permission)

        # Đảm bảo các Permission mới được ghi vào session
        db.flush()

        # 2. Create roles
        for name, description in ROLES:
            role = db.scalar(
                select(Role).where(
                    Role.name == name
                )
            )

            if not role:
                role = Role(
                    name=name,
                    description=description
                )
                db.add(role)

        # Đảm bảo các Role mới được tạo trước khi mapping
        db.flush()

        # 3. Assign permissions to roles
        for role_name, permission_names in role_permissions_map.items():

            role = db.scalar(
                select(Role).where(
                    Role.name == role_name
                )
            )

            if not role:
                continue

            for permission_name in permission_names:

                permission = db.scalar(
                    select(Permission).where(
                        Permission.name == permission_name
                    )
                )

                if permission and permission not in role.permissions:
                    role.permissions.append(permission)

        # 4. Commit
        db.commit()

        print("Seed completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()