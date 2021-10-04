from fastapi import Depends, FastAPI, HTTPException, status

from starlette.responses import RedirectResponse

import pyotp
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import crud, models, schemas
from database import SessionLocal, engine

from security import pwd_context
from utils import *

models.Base.metadata.create_all(bind=engine)

TOTP_EXPIRATION_INTERVAL = 120 #  in seconds

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


def authenticate_user(db: Session, email: str, password: str = None, totp_key: str = None):
    user = get_user(db, email)
    if not user:
        # print ('user not found')
        return False
    if password:
        if not verify_password(password, user.hashed_password):
            # print ('passsword not match')
            return False
    if totp_key:
        totp = pyotp.TOTP(user.otp_secret, interval= TOTP_EXPIRATION_INTERVAL)
        if not totp.verify(totp_key):
            # print ('totp not match')
            return False
    return user


@app.post("/users/create/")
def create_new_user(user: schemas.UserCreate):
    add_temp_user(user)
    one_time_url = create_url_for('create', user.email)
    return {'detail':'Open the url to complete creating user',
     'one_time_url': one_time_url}


@app.post("/users/create/mfa/") #{one_time_url}")
def create_new_user_mfa(password_again: schemas.UserCreateMFA, one_time_url: str, db: Session = Depends(get_db)):
    email = get_email_from_one_time_url(one_time_url)
    temp_user= get_temp_user(email)
    if temp_user:
        if temp_user.password == password_again.password_again: # confirm passwords
            try:
                db_user = crud.create_user(db, temp_user)
            except IntegrityError:
                return {'detail': 'User already exist, try login'}
            remove_temp_user(email) # from memory
            totp = pyotp.TOTP(db_user.otp_secret, interval= TOTP_EXPIRATION_INTERVAL)
            return {'detail': 'User successfully created', 
            'totp_code': totp.now(),
            "expires": str(TOTP_EXPIRATION_INTERVAL) +' Sec'}
        else:
            return {'detail': 'Incorrect password'}
    else:
        return {'detail': 'User not found. Please register.'}


@app.post("/users/mfa/new_totp_code")
def get_new_totp_code(user: schemas.NewTOTPCode, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if db_user:
        totp = pyotp.TOTP(db_user.otp_secret, interval= TOTP_EXPIRATION_INTERVAL)
        return {'detail': 'TOTP renewed', 
        'totp_code': totp.now(),
        "expires":  str(TOTP_EXPIRATION_INTERVAL) +' Sec'}
    else:
        return {'detail': 'No account or incorrect credentials'}


@app.post("/users/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email)
    if db_user:
        one_time_url = create_url_for('login', user.email)
        return {'detail':'Open the url to login', 'one_time_url': one_time_url}
    else:
        return {'detail': 'User not found'}



@app.post("/users/login/mfa/")
def login_fma (user: schemas.UserLoginMFA, one_time_url: str , db: Session = Depends(get_db)):
    email = get_email_from_one_time_url(one_time_url)
    db_user = authenticate_user(db, email, user.password, user.totp_code)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password or invalid totp_code. Please try again or get a new totp code at users/mfa/new_totp_code"
        )
    last_login = '2021.10.2 10:30:23'
    return {'detail': 'Login Successful', 'last-login':last_login}
    


@app.post("/users/delete/")
def delete_user(user: schemas.UserDelete, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if user:
        one_time_url = create_url_for('delete',db_user.email)
        return {'detail': 'Open the url to delete account',
            'one_time_url': one_time_url}
    else:
        return {'detail': 'Incorrect credentials'}


@app.get("/users/delete/mfa")
def delete_user_with_one_time_url(one_time_url: str, db: Session = Depends(get_db)):
    email = get_email_from_one_time_url(one_time_url)
    success = crud.delete_user(db, email)
    if success:
        return {'detail': 'Account successfully deleted'}
    else:
        return {'detail': 'Account not found'}
