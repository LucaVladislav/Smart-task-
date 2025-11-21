from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

# IMPORTANT: aceeași cheie și același algoritm ca în api-gateway/app/auth.py
SECRET_KEY = "SMARTTASK_DEMO_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_for_bcrypt(password: str) -> str:
    data = password.encode("utf-8")
    if len(data) > 72:
        data = data[:72]
    return data.decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    password = _truncate_for_bcrypt(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _truncate_for_bcrypt(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
