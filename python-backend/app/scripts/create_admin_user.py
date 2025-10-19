"""CLI utility to provision administrator accounts securely."""

from __future__ import annotations

import argparse
import getpass
import sys

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.repositories.users_repo import UserRepository
from app.utils.hashing import hash_password


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an initial administrator account without relying on demo credentials."
        )
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Username for the administrator account.",
    )
    parser.add_argument(
        "--password",
        help="Password for the administrator account. If omitted you will be prompted securely.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    password = args.password or getpass.getpass("Password: ")
    if not password:
        print("Error: password cannot be empty.", file=sys.stderr)
        return 1

    settings = get_settings()
    if settings.create_demo_user:
        print(
            "Warning: CREATE_DEMO_USER is enabled. Disable it in production environments to avoid installing demo credentials.",
            file=sys.stderr,
        )

    session = SessionLocal()
    try:
        repository = UserRepository(session)
        if repository.get_by_username(args.username):
            print(
                f"User '{args.username}' already exists. Choose a different username or reset the password instead.",
                file=sys.stderr,
            )
            return 1

        repository.create(
            username=args.username,
            hashed_password=hash_password(password),
        )
    finally:
        session.close()

    print(
        "Administrator account created successfully. Store the credentials securely and distribute them over a trusted channel."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
