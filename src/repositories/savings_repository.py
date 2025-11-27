from typing import Optional, List, Dict, Any
from ..config.json_db import JSONDatabase


class SavingsRepository:
    """
    Repositorio para operaciones CRUD de sobres de ahorro.
    Maneja el acceso a datos de sobres de ahorro en la base de datos JSON.
    """
    
    def __init__(self, db: JSONDatabase):
        self.db = db
        self.collection = "savings_envelopes"
    
    def create(self, savings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo sobre de ahorro"""
        return self.db.create(self.collection, savings_data)
    
    def get_by_id(self, savings_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un sobre de ahorro por su ID"""
        return self.db.read_by_id(self.collection, savings_id)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Obtiene todos los sobres de ahorro"""
        return self.db.read_all(self.collection)
    
    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los sobres de ahorro de un usuario"""
        return self.db.find_many(self.collection, user_id=user_id)
    
    def update(self, savings_id: int, savings_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un sobre de ahorro existente"""
        return self.db.update(self.collection, savings_id, savings_data)
    
    def delete(self, savings_id: int) -> bool:
        """Elimina un sobre de ahorro"""
        return self.db.delete(self.collection, savings_id)
    
    def delete_by_user(self, user_id: int) -> int:
        """Elimina todos los sobres de ahorro de un usuario"""
        envelopes = self.get_by_user(user_id)
        count = 0
        for envelope in envelopes:
            if self.delete(envelope['id']):
                count += 1
        return count
    
    def get_total_savings_by_user(self, user_id: int) -> float:
        """Calcula el total ahorrado por un usuario"""
        envelopes = self.get_by_user(user_id)
        return sum(envelope.get('current_amount', 0.0) for envelope in envelopes)
    
    def get_average_progress_by_user(self, user_id: int) -> float:
        """Calcula el progreso promedio de ahorro de un usuario"""
        envelopes = self.get_by_user(user_id)
        if not envelopes:
            return 0.0
        
        total_progress = 0.0
        for envelope in envelopes:
            target = envelope.get('target_amount', 0.0)
            current = envelope.get('current_amount', 0.0)
            if target > 0:
                progress = (current / target) * 100
                total_progress += progress
        
        return total_progress / len(envelopes)