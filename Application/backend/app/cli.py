from __future__ import annotations

import argparse

from .db import Base, SessionLocal, engine
from .seed import seed


def main() -> None:
    parser = argparse.ArgumentParser(description="Usiri API maintenance commands")
    parser.add_argument("command", choices=["init-db", "seed", "reset"])
    args = parser.parse_args()

    if args.command == "init-db":
        Base.metadata.create_all(engine)
        print("Schema created")
        return

    if args.command == "reset":
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        with SessionLocal() as db:
            seed(db, reset=False)
        print("Database reset and seeded")
        return

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    print("Seed complete")


if __name__ == "__main__":
    main()
