import base64
import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError
from .config import settings

def _prepare(password: str) -> bytes:
    # SHA-256 pre-hash avoids bcrypt's 72-byte limit
    return base64.b64encode(hashlib.sha256(password.encode()).digest())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare(password), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_prepare(plain), hashed.encode())

def create_access_token(sub: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": sub, "role": role, "exp": expire},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise  # поймаем выше в зависимости
