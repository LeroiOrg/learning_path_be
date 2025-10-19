import jwt
import os
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def decode_access_token(token: str):
    """
    Decodifica un token JWT usando PyJWT (misma librería que lo creó).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except InvalidTokenError:
        raise HTTPException(status_code=403, detail="Token inválido")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependencia que valida el JWT y retorna los datos del usuario autenticado.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    email = payload.get("email")
    if not user_id or not email:
        raise HTTPException(status_code=403, detail="Token inválido")
    return {"user_id": user_id, "email": email}
