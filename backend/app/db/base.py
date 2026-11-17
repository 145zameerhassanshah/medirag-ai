"""Database declarative base and identifiers."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass

def sid():
    return str(uuid.uuid4())

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)
