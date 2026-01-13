"""
Utility to populate the database with demo data.
"""

import asyncio

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.init_db import init_db


def main():
    with SessionLocal() as db:
        init_db(db)
        print("Seed data inserted.")


if __name__ == "__main__":
    main()

