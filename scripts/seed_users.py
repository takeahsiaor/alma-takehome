import logging
import os
import sys

sys.path.append(os.path.abspath("."))  # Make imports from app work

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

logger = logging.getLogger(__name__)


def seed():
    db = SessionLocal()

    seeds = [
        ('attorney1@alma.com', True),
        ('attorney2@alma.com', True),
        ('attorney3@alma.com', False),
        ('attorney4@alma.com', False)
    ]

    for email, can_intake in seeds:
        password = "supersecure"

        existing_user = db.query(User).filter_by(email=email).first()
        if existing_user:
            logger.warning("User already exists.")
            continue

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            can_intake=can_intake
        )

        db.add(user)
        logger.info("User created:", email)

    db.commit()

if __name__ == "__main__":
    seed()
