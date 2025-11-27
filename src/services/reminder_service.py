from typing import List, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from ..repositories.reminder_repository import ReminderRepository
from ..dtos.reminder_dto import PaymentReminderCreate, PaymentReminderUpdate


class ReminderService:
    """
    Servicio de recordatorios de pago.
    Maneja la lógica de negocio para recordatorios de pago.
    """

    def __init__(self, reminder_repo: ReminderRepository):
        self.reminder_repo = reminder_repo

    def create_reminder(self, user_id: int, reminder_data: PaymentReminderCreate) -> Dict[str, Any]:
        """
        Crea un nuevo recordatorio de pago.

        Args:
            user_id: ID del usuario
            reminder_data: Datos del recordatorio

        Returns:
            Dict con el recordatorio creado
        """
        reminder_dict = reminder_data.model_dump()
        reminder_dict['user_id'] = user_id

        # Convertir enum a string
        reminder_dict['priority'] = reminder_dict['priority'].value

        # Convertir fecha a ISO string
        reminder_dict['due_date'] = reminder_dict['due_date'].isoformat()

        return self.reminder_repo.create(reminder_dict)

    def get_reminders_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los recordatorios de un usuario.
        Agrega el campo is_overdue a cada recordatorio.
        """
        reminders = self.reminder_repo.get_by_user(user_id)
        now = datetime.utcnow()

        # Agregar campo is_overdue a cada recordatorio
        for reminder in reminders:
            due_date_str = reminder.get('due_date')
            is_paid = reminder.get('is_paid', False)

            if due_date_str and not is_paid:
                due_date = datetime.fromisoformat(
                    due_date_str.replace('Z', '+00:00'))
                reminder['is_overdue'] = due_date < now
            else:
                reminder['is_overdue'] = False

        return reminders

    def get_reminder_by_id(self, user_id: int, reminder_id: int) -> Dict[str, Any]:
        """
        Obtiene un recordatorio específico.

        Args:
            user_id: ID del usuario
            reminder_id: ID del recordatorio

        Returns:
            Dict con el recordatorio

        Raises:
            HTTPException: Si el recordatorio no existe o no pertenece al usuario
        """
        reminder = self.reminder_repo.get_by_id(reminder_id)

        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment reminder not found"
            )

        if reminder['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this payment reminder"
            )

        # Agregar campo is_overdue
        due_date_str = reminder.get('due_date')
        is_paid = reminder.get('is_paid', False)

        if due_date_str and not is_paid:
            due_date = datetime.fromisoformat(
                due_date_str.replace('Z', '+00:00'))
            reminder['is_overdue'] = due_date < datetime.utcnow()
        else:
            reminder['is_overdue'] = False

        return reminder

    def update_reminder(
        self,
        user_id: int,
        reminder_id: int,
        reminder_data: PaymentReminderUpdate
    ) -> Dict[str, Any]:
        """
        Actualiza un recordatorio existente.

        Args:
            user_id: ID del usuario
            reminder_id: ID del recordatorio
            reminder_data: Nuevos datos del recordatorio

        Returns:
            Dict con el recordatorio actualizado
        """
        # Verificar que el recordatorio existe y pertenece al usuario
        existing = self.get_reminder_by_id(user_id, reminder_id)

        # Actualizar solo los campos proporcionados
        update_dict = reminder_data.model_dump(exclude_unset=True)

        # Convertir enum a string si está presente
        if 'priority' in update_dict and update_dict['priority']:
            update_dict['priority'] = update_dict['priority'].value

        # Convertir fecha a ISO string si está presente
        if 'due_date' in update_dict and update_dict['due_date']:
            update_dict['due_date'] = update_dict['due_date'].isoformat()

        existing.update(update_dict)

        return self.reminder_repo.update(reminder_id, existing)

    def delete_reminder(self, user_id: int, reminder_id: int) -> bool:
        """
        Elimina un recordatorio.

        Args:
            user_id: ID del usuario
            reminder_id: ID del recordatorio

        Returns:
            True si se eliminó correctamente
        """
        # Verificar que el recordatorio existe y pertenece al usuario
        self.get_reminder_by_id(user_id, reminder_id)

        return self.reminder_repo.delete(reminder_id)

    def mark_as_paid(self, user_id: int, reminder_id: int) -> Dict[str, Any]:
        """
        Marca un recordatorio como pagado.

        Args:
            user_id: ID del usuario
            reminder_id: ID del recordatorio

        Returns:
            Dict con el recordatorio actualizado
        """
        reminder = self.get_reminder_by_id(user_id, reminder_id)
        reminder['is_paid'] = True

        return self.reminder_repo.update(reminder_id, reminder)

    def get_pending_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene los recordatorios pendientes de un usuario"""
        reminders = self.reminder_repo.get_pending_by_user(user_id)
        now = datetime.utcnow()

        # Agregar campo is_overdue
        for reminder in reminders:
            due_date_str = reminder.get('due_date')
            if due_date_str:
                due_date = datetime.fromisoformat(
                    due_date_str.replace('Z', '+00:00'))
                reminder['is_overdue'] = due_date < now
            else:
                reminder['is_overdue'] = False

        return reminders

    def get_overdue_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene los recordatorios vencidos de un usuario"""
        reminders = self.reminder_repo.get_overdue_by_user(user_id)

        # Agregar campo is_overdue (siempre True para estos)
        for reminder in reminders:
            reminder['is_overdue'] = True

        return reminders
