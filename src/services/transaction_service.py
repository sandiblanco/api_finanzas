from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException, status
from ..repositories.transaction_repository import TransactionRepository
from ..repositories.card_repository import CardRepository
from ..dtos.transaction_dto import TransactionCreate, TransactionUpdate


class TransactionService:
    """
    Servicio de transacciones.
    Maneja la lógica de negocio para transacciones financieras.
    """

    def __init__(self, transaction_repo: TransactionRepository, card_repo: CardRepository):
        self.transaction_repo = transaction_repo
        self.card_repo = card_repo

    def create_transaction(self, user_id: int, transaction_data: TransactionCreate) -> Dict[str, Any]:
        """
        Crea una nueva transacción.

        Args:
            user_id: ID del usuario
            transaction_data: Datos de la transacción

        Returns:
            Dict con la transacción creada
        """
        # Verificar que la tarjeta existe si se especificó una
        if transaction_data.card_id:
            card = self.card_repo.get_by_id(transaction_data.card_id)
            if not card or card['user_id'] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Card not found"
                )

        transaction_dict = transaction_data.model_dump()
        transaction_dict['user_id'] = user_id

        # Si no se especifica fecha, usar la actual
        if not transaction_dict.get('transaction_date'):
            transaction_dict['transaction_date'] = datetime.utcnow(
            ).isoformat()
        else:
            transaction_dict['transaction_date'] = transaction_dict['transaction_date'].isoformat(
            )

        # Convertir enums a strings
        transaction_dict['transaction_type'] = transaction_dict['transaction_type'].value
        transaction_dict['payment_method'] = transaction_dict['payment_method'].value

        return self.transaction_repo.create(transaction_dict)

    def get_transactions_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las transacciones de un usuario"""
        return self.transaction_repo.get_by_user(user_id)

    def get_transaction_by_id(self, user_id: int, transaction_id: int) -> Dict[str, Any]:
        """
        Obtiene una transacción específica.

        Args:
            user_id: ID del usuario
            transaction_id: ID de la transacción

        Returns:
            Dict con la transacción

        Raises:
            HTTPException: Si la transacción no existe o no pertenece al usuario
        """
        transaction = self.transaction_repo.get_by_id(transaction_id)

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        if transaction['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this transaction"
            )

        return transaction

    def update_transaction(
        self,
        user_id: int,
        transaction_id: int,
        transaction_data: TransactionUpdate
    ) -> Dict[str, Any]:
        """
        Actualiza una transacción existente.

        Args:
            user_id: ID del usuario
            transaction_id: ID de la transacción
            transaction_data: Nuevos datos de la transacción

        Returns:
            Dict con la transacción actualizada
        """
        # Verificar que la transacción existe y pertenece al usuario
        existing = self.get_transaction_by_id(user_id, transaction_id)

        # Actualizar solo los campos proporcionados
        update_dict = transaction_data.model_dump(exclude_unset=True)

        # Convertir enums a strings si están presentes
        if 'transaction_type' in update_dict and update_dict['transaction_type']:
            update_dict['transaction_type'] = update_dict['transaction_type'].value

        if 'payment_method' in update_dict and update_dict['payment_method']:
            update_dict['payment_method'] = update_dict['payment_method'].value

        if 'transaction_date' in update_dict and update_dict['transaction_date']:
            update_dict['transaction_date'] = update_dict['transaction_date'].isoformat()

        # Verificar tarjeta si se especificó
        if 'card_id' in update_dict and update_dict['card_id']:
            card = self.card_repo.get_by_id(update_dict['card_id'])
            if not card or card['user_id'] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Card not found"
                )

        # Combinar datos existentes con actualizados
        existing.update(update_dict)

        return self.transaction_repo.update(transaction_id, existing)

    def delete_transaction(self, user_id: int, transaction_id: int) -> bool:
        """
        Elimina una transacción.

        Args:
            user_id: ID del usuario
            transaction_id: ID de la transacción

        Returns:
            True si se eliminó correctamente
        """
        # Verificar que la transacción existe y pertenece al usuario
        self.get_transaction_by_id(user_id, transaction_id)

        return self.transaction_repo.delete(transaction_id)
