"""
Bootstrap the first Super Admin account.

Admins are never self-registered through the public API (only residents
are, and even then they start `pending`) — someone has to exist to approve
registrations and create other admins in the first place. Run this once
per environment:

    cd backend
    python -m scripts.create_admin --name "Ali Khan" --email ali@ehs.example --password "changeme123" --role super_admin
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.admin import Admin  # noqa: E402
from app.models.enums import AdminRole  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an EHS Connect admin account.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument(
        "--role",
        required=True,
        choices=[r.value for r in AdminRole],
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if db.query(Admin).filter(Admin.email == args.email).first():
            print(f"An admin with email {args.email} already exists.", file=sys.stderr)
            sys.exit(1)

        admin = Admin(
            full_name=args.name,
            email=args.email,
            password_hash=hash_password(args.password),
            role=AdminRole(args.role),
        )
        db.add(admin)
        db.commit()
        print(f"Created admin '{admin.full_name}' <{admin.email}> with role {admin.role.value}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
