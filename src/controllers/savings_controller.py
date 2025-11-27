from fastapi import APIRouter, Depends, status
from typing import Dict, Any
from pydantic import BaseModel
from ..services.savings_service import SavingsService
from ..repositories.savings_repository import SavingsRepository
from ..dtos.savings_dto import (
    SavingsEnvelopeCreate,
    SavingsEnvelopeUpdate,
    SavingsEnvelopeResponse,
    SavingsEnvelopeListResponse
)
from ..config.json_db import get_db, JSONDatabase
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/savings-envelopes", tags=["Savings Envelopes"])


class AddAmountRequest(BaseModel):
    """Schema para agregar dinero a un sobre"""
    amount: float


def get_savings_service(db: JSONDatabase = Depends(get_db)) -> SavingsService:
    """Dependency para obtener el servicio de sobres de ahorro"""
    savings_repo = SavingsRepository(db)
    return SavingsService(savings_repo)


@router.post("", response_model=SavingsEnvelopeResponse, status_code=status.HTTP_201_CREATED)
async def create_savings_envelope(
    envelope_data: SavingsEnvelopeCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    savings_service: SavingsService = Depends(get_savings_service)
):
    """
    Crea un nuevo sobre de ahorro.
    
    - **name**: Nombre del sobre
    - **target_amount**: Meta de ahorro
    - **current_amount**: Cantidad inicial (opcional, por defecto 0)
    - **description**: Descripción (opcional)
    """
    user_id = current_user['id']
    return savings_service.create_envelope(user_id, envelope_data)


@router.get("", response_model=SavingsEnvelopeListResponse)
async def get_savings_envelopes(
    current_user: Dict[str, Any] = Depends(get_current_user),
    savings_service: SavingsService = Depends(get_savings_service)
):
    """
    Obtiene todos los sobres de ahorro del usuario autenticado.
    """
    user_id = current_user['id']
    envelopes = savings_service.get_envelopes_by_user(user_id)
    return SavingsEnvelopeListResponse(total=len(envelopes), envelopes=envelopes)


@router.get("/{envelope_id}", response_model=SavingsEnvelopeResponse)
async def get_savings_envelope(
    envelope_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    savings_service: SavingsService = Depends(get_savings_service)
):
    """
    Obtiene un sobre de ahorro específico por su ID.
    """
    user_id = current_user['id']
    return savings_service.get_envelope_by_id(user_id, envelope_id)


@router.put("/{envelope_id}", response_model=SavingsEnvelopeResponse)
async def update_savings_envelope(
    envelope_id: int,
    envelope_data: SavingsEnvelopeUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    savings_service: SavingsService = Depends(get_savings_service)
):
    """
    Actualiza un sobre de ahorro existente.
    
    Solo se actualizan los campos proporcionados.
    """
    user_id = current_user['id']
    return savings_service.update_envelope(user_id, envelope_id, envelope_data)


@router.delete("/{envelope_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_savings_envelope(
    envelope_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    savings_service: SavingsService = Depends(get_savings_service)
):
    """
    Elimina un sobre de ahorro.
    """
    user_id = current_user['id']
    savings_service.delete_envelope(user_id, envelope_id)
    return None


@router.post("/{envelope_id}/add-amount", response_model=SavingsEnvelopeResponse)
async def add_amount_to_envelope(
    envelope_id: int,
    request: AddAmountRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    savings_service: SavingsService = Depends(get_savings_service)
):
    """
    Agrega dinero a un sobre de ahorro.
    
    - **amount**: Cantidad a agregar (debe ser mayor que 0)
    """
    user_id = current_user['id']
    return savings_service.add_amount(user_id, envelope_id, request.amount)