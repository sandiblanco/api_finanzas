from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any
from ..config.json_db import get_db, JSONDatabase
from ..utils.security import decode_access_token

# Esquema OAuth2 para obtener el token del header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: JSONDatabase = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency para obtener el usuario actual desde el token JWT.

    Args:
        token: Token JWT del header Authorization
        db: Instancia de la base de datos JSON

    Returns:
        Dict: Datos del usuario autenticado

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decodificar el token
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception

    # Buscar el usuario en la base de datos
    user = db.find_one("users", username=username)
    if user is None:
        raise credentials_exception

    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency para verificar que el usuario está activo.

    Args:
        current_user: Usuario actual

    Returns:
        Dict: Usuario activo

    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
