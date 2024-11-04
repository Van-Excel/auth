from passlib.context import CryptContext
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import os
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = os.environ.get(
    "SECRET_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")
algorithm = "HS256"

# special characters
special_characters = [
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
    "-",
    "_",
    "=",
    "+",
    "[",
    "]",
    "{",
    "}",
    "|",
    ";",
    ":",
    "'",
    '"',
    ",",
    ".",
    "<",
    ">",
    "/",
    "?",
    "\\",
    "`",
    "~",
]


def encryptPassword(password: str):
    encrypted_password = pwd_context.hash(password)
    return encrypted_password


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def password_is_strong(password: str):
    if len(password) < 8:
        return False

    if not any(char.isupper() for char in password):
        return False

    if not any(char.islower() for char in password):
        return False

    if not any(char.isdigit() for char in password):
        return False

    if not any(char in special_characters for char in password):
        return False

    return True


# generate and verify token

# generate and verify token


def create_token(user:str):
    # we needed to use some claims of newly registered user to create token so we can use it during verification
    payload = {
        "user_email": user,
        "exp":datetime.now() + timedelta(minutes=15)
        }
    token = jwt.encode(payload, secret, algorithm=algorithm)
    return token

def verify_token(token:str, user_email:str):
    # we use user data and expiration time to verify token
    try:
        
        user_payload:dict = jwt.decode(token, secret, algorithms= [algorithm])
        
        
    except ExpiredSignatureError:
        # token expired
        return "token expired"
    except InvalidTokenError:
        #Token is invalid
        return "Invalid token"
    if user_payload.get("user_email") != user_email:
      
        return False
    return True


def create_access_token(data:dict, expires_delta:timedelta = None):
    payload = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    payload.update({"exp": expire})
    access_token = jwt.encode(payload, JWT_SECRET, algorithm=algorithm)
    return access_token





def create_refresh_token(data:dict, expires_delta:timedelta = None):
    payload = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=7)

    payload.update({"exp": expire})
    refresh_token = jwt.encode(payload, JWT_SECRET, algorithm=algorithm)
    return refresh_token


def verify_access_token(token:str):
    # you use the user data encoded in the token for verification
    # decode the data and use it
    pass

    


    
    

