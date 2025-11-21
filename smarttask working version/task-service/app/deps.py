# task-service/app/deps.py

from fastapi import Header, HTTPException, status

from .auth import decode_access_token


def get_current_user(authorization: str = Header(None)):
    """
    Task-service verifică direct JWT-ul primit de la API Gateway.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)

    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return {
        "user_id": payload["user_id"],
        "email": payload.get("sub"),
    }
