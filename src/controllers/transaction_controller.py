from fastapi import APIRouter, Depends, status
from typing import Dict, Any, List
from ..services.transaction_service import TransactionService
from ..repositories.transaction_repository import TransactionRepository
from ..repositories.card_repository import CardRepository
from ..dtos.transaction_dto import (
    TransactionCreate, 
    TransactionUpdate, 
    TransactionResponse,
    TransactionListResponse
)
from ..config.json_db import get_db, JSONDatabase
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_transaction_service(db: JSONDatabase = Depends(get_db)) -> TransactionService:
    """Dependency para obtener el servicio de transacciones"""
    transaction_repo = TransactionRepository(db)
    card_repo = CardRepository(db)
    return TransactionService(transaction_repo, card_repo)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Crea una nueva transacción financiera.
    
    - **category**: Categoría de la transacción
    - **description**: Descripción detallada (opcional)
    - **amount**: Monto de la transacción
    - **transaction_type**: Tipo (income o expense)
    - **payment_method**: Método de pago (cash o card)
    - **card_id**: ID de la tarjeta (opcional, requerido si payment_method es card)
    - **transaction_date**: Fecha de la transacción (opcional, por defecto hoy)
    """
    user_id = current_user['id']
    return transaction_service.create_transaction(user_id, transaction_data)


@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Obtiene todas las transacciones del usuario autenticado.
    """
    user_id = current_user['id']
    transactions = transaction_service.get_transactions_by_user(user_id)
    return TransactionListResponse(total=len(transactions), transactions=transactions)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Obtiene una transacción específica por su ID.
    """
    user_id = current_user['id']
    return transaction_service.get_transaction_by_id(user_id, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Actualiza una transacción existente.
    
    Solo se actualizan los campos proporcionados.
    """
    user_id = current_user['id']
    return transaction_service.update_transaction(user_id, transaction_id, transaction_data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """
    Elimina una transacción.
    """
    user_id = current_user['id']
    transaction_service.delete_transaction(user_id, transaction_id)
    return None