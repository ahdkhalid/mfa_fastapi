from sqlalchemy.orm import Session
import pyotp

import models, schemas
from security import pwd_context


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        otp_secret=pyotp.random_base32()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def delete_user(db: Session, email: str):
    db_user = get_user_by_email(db, email)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    else:
        return False
