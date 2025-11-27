from fastapi import APIRouter, Depends, status
from typing import Dict, Any
from ..services.reminder_service import ReminderService
from ..repositories.reminder_repository import ReminderRepository
from ..dtos.reminder_dto import (
    PaymentReminderCreate,
    PaymentReminderUpdate,
    PaymentReminderResponse,
    PaymentReminderListResponse
)
from ..config.json_db import get_db, JSONDatabase
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/payment-reminders", tags=["Payment Reminders"])


def get_reminder_service(db: JSONDatabase = Depends(get_db)) -> ReminderService:
    """Dependency para obtener el servicio de recordatorios"""
    reminder_repo = ReminderRepository(db)
    return ReminderService(reminder_repo)


@router.post("", response_model=PaymentReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_reminder(
    reminder_data: PaymentReminderCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Crea un nuevo recordatorio de pago.
    
    - **payment_name**: Nombre del pago
    - **amount**: Monto a pagar
    - **due_date**: Fecha de vencimiento
    - **category**: Categoría del pago
    - **priority**: Prioridad (low, medium, high)
    - **is_paid**: Estado de pago (opcional, por defecto false)
    - **description**: Descripción adicional (opcional)
    """
    user_id = current_user['id']
    return reminder_service.create_reminder(user_id, reminder_data)


@router.get("", response_model=PaymentReminderListResponse)
async def get_payment_reminders(
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Obtiene todos los recordatorios de pago del usuario autenticado.
    """
    user_id = current_user['id']
    reminders = reminder_service.get_reminders_by_user(user_id)
    return PaymentReminderListResponse(total=len(reminders), reminders=reminders)


@router.get("/pending", response_model=PaymentReminderListResponse)
async def get_pending_reminders(
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Obtiene los recordatorios pendientes (no pagados) del usuario.
    """
    user_id = current_user['id']
    reminders = reminder_service.get_pending_reminders(user_id)
    return PaymentReminderListResponse(total=len(reminders), reminders=reminders)


@router.get("/overdue", response_model=PaymentReminderListResponse)
async def get_overdue_reminders(
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Obtiene los recordatorios vencidos del usuario.
    """
    user_id = current_user['id']
    reminders = reminder_service.get_overdue_reminders(user_id)
    return PaymentReminderListResponse(total=len(reminders), reminders=reminders)


@router.get("/{reminder_id}", response_model=PaymentReminderResponse)
async def get_payment_reminder(
    reminder_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Obtiene un recordatorio de pago específico por su ID.
    """
    user_id = current_user['id']
    return reminder_service.get_reminder_by_id(user_id, reminder_id)


@router.put("/{reminder_id}", response_model=PaymentReminderResponse)
async def update_payment_reminder(
    reminder_id: int,
    reminder_data: PaymentReminderUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Actualiza un recordatorio de pago existente.
    
    Solo se actualizan los campos proporcionados.
    """
    user_id = current_user['id']
    return reminder_service.update_reminder(user_id, reminder_id, reminder_data)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_reminder(
    reminder_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Elimina un recordatorio de pago.
    """
    user_id = current_user['id']
    reminder_service.delete_reminder(user_id, reminder_id)
    return None


@router.patch("/{reminder_id}/mark-paid", response_model=PaymentReminderResponse)
async def mark_reminder_as_paid(
    reminder_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    reminder_service: ReminderService = Depends(get_reminder_service)
):
    """
    Marca un recordatorio como pagado.
    """
    user_id = current_user['id']
    return reminder_service.mark_as_paid(user_id, reminder_id)