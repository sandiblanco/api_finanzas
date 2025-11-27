from typing import Optional, List, Dict, Any
from datetime import datetime
from ..config.json_db import JSONDatabase


class ReminderRepository:
    """
    Repositorio para operaciones CRUD de recordatorios de pago.
    Maneja el acceso a datos de recordatorios en la base de datos JSON.
    """
    
    def __init__(self, db: JSONDatabase):
        self.db = db
        self.collection = "payment_reminders"
    
    def create(self, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo recordatorio de pago"""
        return self.db.create(self.collection, reminder_data)
    
    def get_by_id(self, reminder_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un recordatorio por su ID"""
        return self.db.read_by_id(self.collection, reminder_id)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Obtiene todos los recordatorios"""
        return self.db.read_all(self.collection)
    
    def get_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los recordatorios de un usuario"""
        return self.db.find_many(self.collection, user_id=user_id)
    
    def get_pending_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene recordatorios pendientes de un usuario"""
        all_reminders = self.get_by_user(user_id)
        return [r for r in all_reminders if not r.get('is_paid', False)]
    
    def get_overdue_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene recordatorios vencidos de un usuario"""
        pending = self.get_pending_by_user(user_id)
        now = datetime.utcnow()
        overdue = []
        
        for reminder in pending:
            due_date_str = reminder.get('due_date')
            if due_date_str:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                if due_date < now:
                    overdue.append(reminder)
        
        return overdue
    
    def get_by_priority(self, user_id: int, priority: str) -> List[Dict[str, Any]]:
        """Obtiene recordatorios de un usuario filtrados por prioridad"""
        all_reminders = self.get_by_user(user_id)
        return [r for r in all_reminders if r.get('priority') == priority]
    
    def update(self, reminder_id: int, reminder_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un recordatorio existente"""
        return self.db.update(self.collection, reminder_id, reminder_data)
    
    def delete(self, reminder_id: int) -> bool:
        """Elimina un recordatorio"""
        return self.db.delete(self.collection, reminder_id)
    
    def delete_by_user(self, user_id: int) -> int:
        """Elimina todos los recordatorios de un usuario"""
        reminders = self.get_by_user(user_id)
        count = 0
        for reminder in reminders:
            if self.delete(reminder['id']):
                count += 1
        return count
    
    def mark_as_paid(self, reminder_id: int) -> Optional[Dict[str, Any]]:
        """Marca un recordatorio como pagado"""
        reminder = self.get_by_id(reminder_id)
        if reminder:
            reminder['is_paid'] = True
            return self.update(reminder_id, reminder)
        return None