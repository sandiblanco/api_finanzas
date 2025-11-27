from fastapi import APIRouter, Depends, status
from typing import Dict, Any
from ..services.card_service import CardService
from ..repositories.card_repository import CardRepository
from ..dtos.card_dto import CardCreate, CardUpdate, CardResponse, CardListResponse
from ..config.json_db import get_db, JSONDatabase
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/cards", tags=["Cards"])


def get_card_service(db: JSONDatabase = Depends(get_db)) -> CardService:
    """Dependency para obtener el servicio de tarjetas"""
    card_repo = CardRepository(db)
    return CardService(card_repo)


@router.post("", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: CardCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    Crea una nueva tarjeta bancaria.
    
    - **bank_name**: Nombre del banco
    - **card_type**: Tipo de tarjeta (débito, crédito, etc.)
    - **last_four_digits**: Últimos 4 dígitos de la tarjeta
    - **balance**: Balance actual (opcional, por defecto 0)
    - **card_holder_name**: Nombre del titular (opcional)
    """
    user_id = current_user['id']
    return card_service.create_card(user_id, card_data)


@router.get("", response_model=CardListResponse)
async def get_cards(
    current_user: Dict[str, Any] = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    Obtiene todas las tarjetas del usuario autenticado.
    """
    user_id = current_user['id']
    cards = card_service.get_cards_by_user(user_id)
    return CardListResponse(total=len(cards), cards=cards)


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    Obtiene una tarjeta específica por su ID.
    """
    user_id = current_user['id']
    return card_service.get_card_by_id(user_id, card_id)


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: int,
    card_data: CardUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    Actualiza una tarjeta existente.
    
    Solo se actualizan los campos proporcionados.
    """
    user_id = current_user['id']
    return card_service.update_card(user_id, card_id, card_data)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    card_service: CardService = Depends(get_card_service)
):
    """
    Elimina una tarjeta.
    """
    user_id = current_user['id']
    card_service.delete_card(user_id, card_id)
    return None