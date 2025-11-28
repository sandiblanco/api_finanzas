from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional
from ..config.json_db import get_db, JSONDatabase
from ..utils.security import decode_access_token

# Esquema OAuth2 (en modo demo, auto_error=False hace que sea opcional)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: JSONDatabase = Depends(get_db)
) -> Dict[str, Any]:
    """
    MODO DEMOSTRACIÓN: Retorna siempre un usuario demo.
    Permite usar todos los endpoints sin autenticación real.
    """
    # Usuario demo por defecto
    demo_user = {
        'id': 1,
        'username': 'demo',
        'email': 'demo@test.com',
        'full_name': 'Usuario Demo',
        'is_active': True
    }
    
    # Si hay token válido, intentar usarlo (opcional)
    if token:
        username = decode_access_token(token)
        if username:
            user = db.find_one("users", username=username)
            if user:
                return user
    
    # Siempre retornar usuario demo si no hay token válido
    return demo_user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retorna el usuario activo (siempre activo en modo demo).
    """
    current_user['is_active'] = True
    return current_user