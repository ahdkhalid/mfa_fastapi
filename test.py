import json
import requests

SIGNUP_ENDPOINT = "http://127.0.0.1:8000/users/create"
LOGIN_ENDPOINT = "http://127.0.0.1:8000/users/login"
DELETE_ENDPOINT = "http://127.0.0.1:8000/users/delete/"
RENEW_TOTP_CODE_ENDPOINT = "http://127.0.0.1:8000/users/mfa/new_totp_code"

headers = {
    "Content-Type": "application/json",
}
user_to_create_email = 'f@gmail.com'



def do_create_user():
    create_data = {
    "email": user_to_create_email,
    "full_name": "TESTT",
    "password": "khalid"
    }
    r = requests.post(SIGNUP_ENDPOINT, data=json.dumps(create_data), headers=headers)

    print (r.status_code)
    print (r.text)
    one_time_url = r.json()['one_time_url']
    return one_time_url


def do_create_user_mfa():
    create_data_mfa = {
    "password_again": "khalid",
    }
    one_time_url = do_create_user()
    r = requests.post(one_time_url, data=json.dumps(create_data_mfa), headers=headers)
    print (r.text)

    totp_code = r.json()['totp_code']
    return totp_code, r.status_code


def do_get_new_totp_code():
    get_new_totp_code_data = {
    "email": user_to_create_email,
    "password": "khalid"
    }
    r = requests.post(RENEW_TOTP_CODE_ENDPOINT, data=json.dumps(get_new_totp_code_data), headers=headers)

    print (r.status_code)
    print (r.text)
    totp_code = r.json()['totp_code']
    return totp_code


def do_login():
    login_data = {
    "email": user_to_create_email
    }
    r = requests.post(LOGIN_ENDPOINT, data=json.dumps(login_data), headers=headers)
    print (r.status_code)
    print (r.text)

    one_time_url = r.json()['one_time_url']
    return one_time_url

def do_login_mfa(totp_code):
    login_data_mfa = {
    "password": 'khalid',
    'totp_code': totp_code
    }
    one_time_url = do_login() +'extrafortest'
    r = requests.post(one_time_url, data=json.dumps(login_data_mfa), headers=headers)

    print (r.text)
    return r.status_code

# totp_code, status = do_create_user_mfa()
# totp_code = do_get_new_totp_code()
# do_login_mfa(totp_code)



def do_delete():
    delete_data = {
    "email": user_to_create_email,
    'password': 'khalid'
    }
    r = requests.post(DELETE_ENDPOINT, data=json.dumps(delete_data), headers=headers)
    print (r.status_code)
    print (r.text)

    one_time_url = r.json()['one_time_url']
    return one_time_url

def do_delete_mfa():
    one_time_url = do_delete()
    r = requests.get(one_time_url)
    print (r.text)

    return r.status_code
# do_delete_mfa()


import unittest  
class TestStringMethods(unittest.TestCase):
    totp_code = 0 
    def setUp(self):
        pass
  
    # Returns 200 when user successfully created, 
    # you need to change user email addresss every time you run the test. 
    # multiple account with same email cannot be created
    def test_create_user_with_mfa_should_200_OK(self):
        global totp_code
        totp_code, status = do_create_user_mfa()
        self.assertEqual(status, 200)
  
    # Returns 200 when user login created
    def test_login_user_with_mfa_should_200_OK(self):
        self.assertEqual(do_login_mfa(totp_code), 200)


if __name__ == '__main__':
    unittest.main()