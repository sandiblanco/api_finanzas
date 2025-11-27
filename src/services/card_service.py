from typing import List, Dict, Any
from fastapi import HTTPException, status
from ..repositories.card_repository import CardRepository
from ..dtos.card_dto import CardCreate, CardUpdate


class CardService:
    """
    Servicio de tarjetas.
    Maneja la lógica de negocio para tarjetas bancarias.
    """
    
    def __init__(self, card_repo: CardRepository):
        self.card_repo = card_repo
    
    def create_card(self, user_id: int, card_data: CardCreate) -> Dict[str, Any]:
        """
        Crea una nueva tarjeta.
        
        Args:
            user_id: ID del usuario
            card_data: Datos de la tarjeta
            
        Returns:
            Dict con la tarjeta creada
        """
        card_dict = card_data.model_dump()
        card_dict['user_id'] = user_id
        
        return self.card_repo.create(card_dict)
    
    def get_cards_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las tarjetas de un usuario"""
        return self.card_repo.get_by_user(user_id)
    
    def get_card_by_id(self, user_id: int, card_id: int) -> Dict[str, Any]:
        """
        Obtiene una tarjeta específica.
        
        Args:
            user_id: ID del usuario
            card_id: ID de la tarjeta
            
        Returns:
            Dict con la tarjeta
            
        Raises:
            HTTPException: Si la tarjeta no existe o no pertenece al usuario
        """
        card = self.card_repo.get_by_id(card_id)
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        if card['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this card"
            )
        
        return card
    
    def update_card(self, user_id: int, card_id: int, card_data: CardUpdate) -> Dict[str, Any]:
        """
        Actualiza una tarjeta existente.
        
        Args:
            user_id: ID del usuario
            card_id: ID de la tarjeta
            card_data: Nuevos datos de la tarjeta
            
        Returns:
            Dict con la tarjeta actualizada
        """
        # Verificar que la tarjeta existe y pertenece al usuario
        existing = self.get_card_by_id(user_id, card_id)
        
        # Actualizar solo los campos proporcionados
        update_dict = card_data.model_dump(exclude_unset=True)
        existing.update(update_dict)
        
        return self.card_repo.update(card_id, existing)
    
    def delete_card(self, user_id: int, card_id: int) -> bool:
        """
        Elimina una tarjeta.
        
        Args:
            user_id: ID del usuario
            card_id: ID de la tarjeta
            
        Returns:
            True si se eliminó correctamente
        """
        # Verificar que la tarjeta existe y pertenece al usuario
        self.get_card_by_id(user_id, card_id)
        
        return self.card_repo.delete(card_id)
    
    def get_total_balance(self, user_id: int) -> float:
        """
        Calcula el balance total de todas las tarjetas de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Balance total
        """
        return self.card_repo.get_total_balance_by_user(user_id)