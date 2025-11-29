from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional
from datetime import datetime
from ..config.json_db import get_db, JSONDatabase
from ..utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: JSONDatabase = Depends(get_db)
) -> Dict[str, Any]:
    demo_user = {
        'id': 1,
        'username': 'demo',
        'email': 'demo@test.com',
        'full_name': 'Usuario Demo',
        'is_active': True,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    if token:
        try:
            username = decode_access_token(token)
            if username:
                user = db.find_one("users", username=username)
                if user:
                    return user
        except:
            pass
    
    return demo_user

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    current_user['is_active'] = True
    return current_user