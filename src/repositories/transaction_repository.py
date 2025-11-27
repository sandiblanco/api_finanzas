from typing import Optional, List, Dict, Any
from datetime import datetime
from ..config.json_db import JSONDatabase


class TransactionRepository:
    """
    Repositorio para operaciones CRUD de transacciones.
    Maneja el acceso a datos de transacciones en la base de datos JSON.
    """
    
    def __init__(self, db: JSONDatabase):
        self.db = db
        self.collection = "transactions"
    
    def create(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva transacción"""
        return self.db.create(self.collection, transaction_data)
    
    def get_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una transacción por su ID"""
        return self.db.read_by_id(self.collection, transaction_id)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Obtiene todas las transacciones"""
        return self.db.read_all(self.collection)
    
    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las transacciones de un usuario"""
        return self.db.find_many(self.collection, user_id=user_id)
    
    def get_by_user_and_type(self, user_id: int, transaction_type: str) -> List[Dict[str, Any]]:
        """Obtiene transacciones de un usuario filtradas por tipo"""
        all_transactions = self.get_by_user(user_id)
        return [t for t in all_transactions if t.get('transaction_type') == transaction_type]
    
    def get_by_user_and_category(self, user_id: int, category: str) -> List[Dict[str, Any]]:
        """Obtiene transacciones de un usuario filtradas por categoría"""
        all_transactions = self.get_by_user(user_id)
        return [t for t in all_transactions if t.get('category') == category]
    
    def get_by_user_and_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Obtiene transacciones de un usuario en un rango de fechas"""
        all_transactions = self.get_by_user(user_id)
        filtered = []
        
        for transaction in all_transactions:
            transaction_date_str = transaction.get('transaction_date')
            if transaction_date_str:
                transaction_date = datetime.fromisoformat(transaction_date_str.replace('Z', '+00:00'))
                if start_date <= transaction_date <= end_date:
                    filtered.append(transaction)
        
        return filtered
    
    def update(self, transaction_id: int, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza una transacción existente"""
        return self.db.update(self.collection, transaction_id, transaction_data)
    
    def delete(self, transaction_id: int) -> bool:
        """Elimina una transacción"""
        return self.db.delete(self.collection, transaction_id)
    
    def delete_by_user(self, user_id: int) -> int:
        """Elimina todas las transacciones de un usuario"""
        transactions = self.get_by_user(user_id)
        count = 0
        for transaction in transactions:
            if self.delete(transaction['id']):
                count += 1
        return count