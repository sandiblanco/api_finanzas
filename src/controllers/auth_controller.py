from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from ..services.auth_service import AuthService
from ..repositories.user_repository import UserRepository
from ..dtos.auth_dto import UserCreate, UserLogin, UserResponse, Token
from ..config.json_db import get_db, JSONDatabase
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: JSONDatabase = Depends(get_db)) -> AuthService:
    """Dependency para obtener el servicio de autenticación"""
    user_repo = UserRepository(db)
    return AuthService(user_repo)


# @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def register(
#     user_data: UserCreate,
#     auth_service: AuthService = Depends(get_auth_service)
# ):
#     """
#     Registra un nuevo usuario.
    
#     - **email**: Email del usuario (único)
#     - **username**: Nombre de usuario (único)
#     - **password**: Contraseña (mínimo 6 caracteres)
#     - **full_name**: Nombre completo (opcional)
#     """
#     return auth_service.register(user_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Inicia sesión y obtiene un token JWT.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna un token de acceso JWT que debe incluirse en el header Authorization
    para las peticiones subsecuentes como: `Bearer {token}`
    """
    credentials = UserLogin(username=form_data.username, password=form_data.password)
    return auth_service.login(credentials)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtiene el perfil del usuario autenticado actual.
    
    Requiere autenticación JWT.
    """
    return current_user