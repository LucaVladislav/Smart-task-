from fastapi import Header, HTTPException, status

from .auth import decode_access_token


def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Extrage JWT din headerul Authorization: Bearer <token>
    și întoarce {user_id, email}.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
        )

    token = parts[1]
    return decode_access_token(token)
