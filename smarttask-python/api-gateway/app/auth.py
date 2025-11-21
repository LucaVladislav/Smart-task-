from typing import Dict, Any

from fastapi import HTTPException, status
from jose import jwt, JWTError

# EXACT aceeași cheie și algoritm ca în user-service/app/auth.py
SECRET_KEY = "SMARTTASK_DEMO_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    sub = payload.get("sub")
    email = payload.get("email")
    if sub is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
        )

    return {"user_id": user_id, "email": email}
