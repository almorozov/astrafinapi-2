from .database import SessionLocal
from . import models

def run() -> None:
    db = SessionLocal()
    try:
        if not db.query(models.Company).filter_by(name="AstraFin Demo").first():
            db.add(models.Company(name="AstraFin Demo", inn="7700000001"))
            db.commit()
    finally:
        db.close()