from typing import Optional, List, Dict, Any
from ..config.json_db import JSONDatabase


class CardRepository:
    """
    Repositorio para operaciones CRUD de tarjetas.
    Maneja el acceso a datos de tarjetas en la base de datos JSON.
    """
    
    def __init__(self, db: JSONDatabase):
        self.db = db
        self.collection = "cards"
    
    def create(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva tarjeta"""
        return self.db.create(self.collection, card_data)
    
    def get_by_id(self, card_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una tarjeta por su ID"""
        return self.db.read_by_id(self.collection, card_id)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Obtiene todas las tarjetas"""
        return self.db.read_all(self.collection)
    
    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las tarjetas de un usuario"""
        return self.db.find_many(self.collection, user_id=user_id)
    
    def get_by_user_and_bank(self, user_id: int, bank_name: str) -> List[Dict[str, Any]]:
        """Obtiene tarjetas de un usuario filtradas por banco"""
        all_cards = self.get_by_user(user_id)
        return [c for c in all_cards if c.get('bank_name') == bank_name]
    
    def update(self, card_id: int, card_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza una tarjeta existente"""
        return self.db.update(self.collection, card_id, card_data)
    
    def delete(self, card_id: int) -> bool:
        """Elimina una tarjeta"""
        return self.db.delete(self.collection, card_id)
    
    def delete_by_user(self, user_id: int) -> int:
        """Elimina todas las tarjetas de un usuario"""
        cards = self.get_by_user(user_id)
        count = 0
        for card in cards:
            if self.delete(card['id']):
                count += 1
        return count
    
    def get_total_balance_by_user(self, user_id: int) -> float:
        """Calcula el balance total de todas las tarjetas de un usuario"""
        cards = self.get_by_user(user_id)
        return sum(card.get('balance', 0.0) for card in cards)