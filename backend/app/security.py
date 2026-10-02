import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import bcrypt
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        return False


def _decode(value: str) -> bytes:
    return base64.b64decode(value, validate=True)


def decrypt_login_payload(encrypted_key: str, iv: str, ciphertext: str) -> dict[str, str]:
    settings = get_settings()
    private_key = serialization.load_pem_private_key(
        Path(settings.auth_private_key_path).read_bytes(), password=None
    )
    aes_key = private_key.decrypt(
        _decode(encrypted_key),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    plaintext = AESGCM(aes_key).decrypt(_decode(iv), _decode(ciphertext), None)
    payload = json.loads(plaintext.decode())
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("email"), str)
        or not isinstance(payload.get("password"), str)
    ):
        raise ValueError("Invalid login payload")
    return {"email": payload["email"].strip().lower(), "password": payload["password"]}


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    return jwt.encode(
        {"sub": user_id, "jti": str(uuid4()), "exp": expires},
        settings.jwt_secret,
        algorithm="HS256",
    )


bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload: dict[str, Any] = jwt.decode(
            credentials.credentials,
            get_settings().jwt_secret,
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise ValueError
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user
