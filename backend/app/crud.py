from sqlalchemy.orm import Session
from . import models, schemas

def get_transactions(db: Session):
    return db.query(models.Transaction).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_trans = models.Transaction(**transaction.dict())
    db.add(db_trans)
    db.commit()
    db.refresh(db_trans)
    return db_trans

def transaction_exists(db: Session, date, description, amount):
    return db.query(models.Transaction).filter_by(
        date=date, description=description, amount=amount
    ).first()
