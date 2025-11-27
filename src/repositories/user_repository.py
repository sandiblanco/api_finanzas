from typing import Optional, List, Dict, Any
from ..config.json_db import JSONDatabase


class UserRepository:
    """
    Repositorio para operaciones CRUD de usuarios.
    Maneja el acceso a datos de usuarios en la base de datos JSON.
    """
    
    def __init__(self, db: JSONDatabase):
        self.db = db
        self.collection = "users"
    
    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo usuario"""
        return self.db.create(self.collection, user_data)
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID"""
        return self.db.read_by_id(self.collection, user_id)
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su nombre de usuario"""
        return self.db.find_one(self.collection, username=username)
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su email"""
        return self.db.find_one(self.collection, email=email)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios"""
        return self.db.read_all(self.collection)
    
    def update(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un usuario existente"""
        return self.db.update(self.collection, user_id, user_data)
    
    def delete(self, user_id: int) -> bool:
        """Elimina un usuario"""
        return self.db.delete(self.collection, user_id)
    
    def exists_by_username(self, username: str) -> bool:
        """Verifica si existe un usuario con el username dado"""
        return self.get_by_username(username) is not None
    
    def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con el email dado"""
        return self.get_by_email(email) is not None