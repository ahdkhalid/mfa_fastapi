from fastapi import Depends, FastAPI, HTTPException

from starlette.responses import RedirectResponse

import pyotp
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

from security import pwd_context
from utils import *

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, email: str):
    return crud.get_user_by_email(db, email)


def authenticate_user(db: Session, email: str, password: str, totp_key: str = None):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if totp_key:
        totp = pyotp.TOTP(user.otp_secret, interval = 120)
        if not totp.verify(totp_key):
            return False
    return user


@app.post("/users/create/")
def create_new_user(user: schemas.UserCreate):
    add_temp_user(user)
    one_time_url = create_url_for('create', user.email)
    return {"one_time_url": one_time_url}



@app.post("/users/create/mfa/")#{one_time_url}")
def create_new_user_mfa(password_again: str, one_time_url: str, db: Session = Depends(get_db)):
    email = get_email_from_one_time_url(one_time_url)
    print (email)
    user= get_temp_user(email)
    if user:
        if user.password == password_again: # confirm passwords
            db_user = crud.create_user(db, user)
            remove_temp_user(email)
            totp = pyotp.TOTP(db_user.otp_secret, interval=120)
            return {'detail': 'User successfully created', 
            'totp code': totp.now(),
            "expires": "2 min"}
        else:
            return {'detail': 'Incorrect password'}
    else:
        return {'detail': 'User not found. Please register.'}


@app.post("/users/mfa/new_totp_code")
def get_new_totp_code(email: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if user:
        totp = pyotp.TOTP(user.otp_secret, interval=120)
        return {'detail': 'TOTP renewed', 
        'totp code': totp.now(),
        "expires": "2 min"}
    else:
        return {'detail': 'No account or incorrect credentials'}


@app.post("/login")
def login(email: str, db: Session = Depends(get_db)):
    one_time_url = create_url_for('login', email)
    
    return {"url": one_time_url}



@app.post("/login/mfa/")
def login_fma (password: str, totp_code: str, one_time_url: str , db: Session = Depends(get_db)):
    email = get_email_from_one_time_url(one_time_url)
    user = authenticate_user(db, email, password, totp_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password or invalid totp_code. Please try again or get a new totp code at users/mfa/new_totp_code"
        )
    last_login = '2021.10.2 10:30:23'
    return {'detail': 'Login Successful', 'last-login':last_login}
    


@app.post("/users/delete/")
def delete_user(user: schemas.UserDelete, db: Session = Depends(get_db)):
    user = authenticate_user(db, user.email, user.password)
    if user:
        one_time_url = create_url_for('delete',user.email)
        return {"one_time_url": one_time_url}
    else:
        return {'detail': 'Incorrect credentials'}


@app.get("/users/delete/")
def delete_user_with_one_time_url(one_time_url: str, db: Session = Depends(get_db)):
    email = get_email_from_one_time_url(one_time_url)
    success = crud.delete_user(db, email)
    if success:
        return {'detail': 'Account successfully deleted'}
    else:
        return {'detail': 'Account not found'}
