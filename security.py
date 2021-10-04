from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


bs64_encode_key = 'LKAJVLO3R32NVX' #minimal security consideration