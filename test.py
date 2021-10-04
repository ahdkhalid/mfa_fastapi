import json
import requests

SIGNUP_ENDPOINT = "http://127.0.0.1:8000/users/create"
SIGNUP_MFA_ENDPOINT = "http://127.0.0.1:8000/users/create/mfa"
USER_EMAILED_ONE_TIME_URL = 'http://127.0.0.1:8000/users/create/mfa/?one_time_url=TEtBSlZMTzNSMzJOVlhnQGdtYWlsLmNvbQ=='
mfa_tmp_url = 'http://127.0.0.1:8000/users/create/mfa/?one_time_url=TEtBSlZMTzNSMzJOVlhnQGdtYWlsLmNvbQ=='

headers = {
    "Content-Type": "application/json",
}

data = {
    "password": "khalid",
    "one_time_url": mfa_tmp_url
}
create_data = {
  "email": "m@yahoo.com",
  "full_name": "M",
  "password": "khalid"
}

r = requests.post(SIGNUP_MFA_ENDPOINT, data=json.dumps(data), headers=headers)

print (r.status_code)
print (r.text)