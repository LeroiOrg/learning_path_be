import jwt
import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def decode_access_token(token: str):
    """
    Decodifica un token de acceso JWT.

    Args:
        token (str): Token JWT a decodificar.

    Returns:
        dict: Datos decodificados del token.

    Raises:
        jwt.ExpiredSignatureError: Si el token ha expirado.
        jwt.InvalidTokenError: Si el token es inválido.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependencia que valida el JWT y retorna el email del usuario autenticado.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=403, detail="Token inválido o expirado")
