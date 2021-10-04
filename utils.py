from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from schemas import UserCreate
from security import bs64_encode_key

temp_user_db = {}

LOGIN_URL_PREFIX ='http://127.0.0.1:8000/login/?one_time_url='
CREATE_USER_URL_PREFIX ='http://127.0.0.1:8000/users/create/mfa/?one_time_url='
DELETE_USER_URL_PREFIX ='http://127.0.0.1:8000/users/delete/?one_time_url='


def add_temp_user(user: UserCreate) -> None:
    temp_user_db [user.email] = {'full_name': user.full_name,
    'password': user.password}

def remove_temp_user(email: str) -> None:
    try:
        del temp_user_db[email]
    except KeyError:
        pass


def get_temp_user(email: str) -> UserCreate:
    print (temp_user_db)
    try:
        full_name = temp_user_db[email]['full_name']
        password = temp_user_db[email]['password']

        user = UserCreate (email = email, full_name = full_name, password = password)
        return user
    except KeyError:
        return None

def base64_encode(email: str) -> str:
    email_in_bytes = (bs64_encode_key+email).encode("ascii")
    
    base64_bytes = b64e(email_in_bytes)
    base64_string = base64_bytes.decode("ascii")
    
    return base64_string


def base64_decode(base64_string: str) -> str:
    base64_string_in_bytes = base64_string.encode("ascii")
    
    email_in_bytes = b64d(base64_string_in_bytes)
    email_string = email_in_bytes.decode("ascii")[14:] # key len
  
    return email_string


def parse_one_time_url(one_time_url: str) -> str:
    try:
        base64_string = one_time_url.split ('one_time_url=')[1]
        return base64_string
    except IndexError: # no need for removing http://... , opening url rather pasting it in field
        return one_time_url


def get_email_from_one_time_url(one_time_url):
    base64_string = parse_one_time_url(one_time_url)
    email = base64_decode(base64_string)

    return email


def create_url_for(who: str, email: str) -> str:
    one_time_url = base64_encode(email)
    if who == 'create':
        url_format = CREATE_USER_URL_PREFIX + one_time_url
    elif who == 'login':
        url_format = LOGIN_URL_PREFIX + one_time_url
    else: # for delete
        url_format = DELETE_USER_URL_PREFIX + one_time_url
    return url_format

