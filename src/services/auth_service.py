from typing import Optional, Dict, Any
from datetime import timedelta
from fastapi import HTTPException, status
from ..repositories.user_repository import UserRepository
from ..utils.security import verify_password, get_password_hash, create_access_token
from ..dtos.auth_dto import UserCreate, UserLogin, Token
from ..config.settings import settings


class AuthService:
    """
    Servicio de autenticación.
    Maneja el registro, login y autenticación de usuarios.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def register(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Registra un nuevo usuario.

        Args:
            user_data: Datos del usuario a registrar

        Returns:
            Dict con los datos del usuario creado

        Raises:
            HTTPException: Si el username o email ya existen
        """
        # Verificar si el usuario ya existe
        if self.user_repo.exists_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        if self.user_repo.exists_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Crear el usuario
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "hashed_password": get_password_hash(user_data.password),
            "is_active": True
        }

        created_user = self.user_repo.create(user_dict)

        # Remover la contraseña hasheada de la respuesta
        created_user.pop('hashed_password', None)

        return created_user

    def login(self, credentials: UserLogin) -> Token:
        """
        Autentica un usuario y genera un token JWT.

        Args:
            credentials: Credenciales de login (username y password)

        Returns:
            Token JWT

        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        # Buscar el usuario
        user = self.user_repo.get_by_username(credentials.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar la contraseña
        if not verify_password(credentials.password, user['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar que el usuario esté activo
        if not user.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        # Crear el token
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['username']},
            expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene el perfil de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Dict con los datos del usuario (sin contraseña)

        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Remover la contraseña hasheada
        user.pop('hashed_password', None)

        return user
