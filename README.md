# Multi Factor Authentication FastAPI - example
This repo is a solution to a challenge for implementing two-factor authentication (One-Time Password) using pyotp and Fast API. It also includes the code for adding a backend user database with SQLAlchemy.\

The repo implements these MFA workflows:
* **ACCOUNT CREATION**: A user can create an account with their email address and password. After these credentials are entered, the user is given (or emailed - will be implemented in next version) a one-time use url that they must visit and again supply password. Upon confirmation of the password, a success message and also a TOTP code will be sent to user that they will need to use when logging into the platform in the future.

* **LOGIN**: A user can login to their account. For that, the user is asked for their email address. Upon receipt of their email address, they are given (or emailed - will be implemented in next version) a one-time use url which they must visit. They must visit/enter one-time url, their password and their TOTP code. Once verified, the user is presented with a success message showing them the last previous time they logged.

* **DELETE ACCOUNT**: User is allowed to delete their account by providng their email address and password. After these credentials are received, the user is emailed a one-time use url and upon visiting this link, the deletion is effected and user is presented with a success message.



## Requirements
I suggest making a Python 3 virtual environment and install the following: 

```
pip install fastapi[all]
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install pyotp
pip install SQLAlchemy
```

## Run
Once installed, clone this repo, you can now run the following command to launch the application:

``` uvicorn --reload main:app ```

When server start running, go to (http://127.0.0.1:8000/docs) to interact with the API. 
You can also use your own tool to interect with API.

### ENDPOINTS

* **POST** 
​/users​/create​/\
Supply an email, you will be given a one-time link to visit. 

* **POST** 
​/users​/create​/mfa​/\
Upon visiting the one-time link, supply your password again. User will be created if passwords match and you are given a totp code to use when login.

* **POST** 
​/users​/mfa​/new_totp_code/\
When totp code expires, you can get a new one by supplying your email and password.

* **POST** 
​/users​/login/\
Login to your account by supplying your email. you will be given a link to complete login.

* **POST** 
​/users​/login​/mfa​/\
Upon visiing the link, you need to supply your password and totp code to login.

* **POST** 
​/users​/delete​/\
Delete your account by supplying your email and password. you will be given a link, by visiting the link, delete procedure will take effect.

* **GET** 
​/users​/delete​/mfa/\
Upon visiting the link, your account will be deleted. \
\
Note that, in this repo one-time urls are given in the response message. But to do real MFA, we must email the one-time urls to user and proceed as that way. By adding a email module, this repo will be complete.
