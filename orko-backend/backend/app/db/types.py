# backend/app/db/types.py
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import JSON as SAJSON

try:
    # Available when the dialect is PostgreSQL
    from sqlalchemy.dialects.postgresql import JSONB as PGJSONB
except Exception:  # pragma: no cover
    PGJSONB = None  # not on this interpreter, fine for non-PG

class JSONType(TypeDecorator):
    """
    Portable JSON/JSONB:
      • On PostgreSQL → uses native JSONB
      • On all other DBs (SQLite for tests) → uses SQLAlchemy JSON (TEXT/JSON1)
    """
    impl = SAJSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and PGJSONB is not None:
            return dialect.type_descriptor(PGJSONB())
        # SQLite / others
        return dialect.type_descriptor(SAJSON())
