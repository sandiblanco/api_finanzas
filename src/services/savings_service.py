from typing import List, Dict, Any
from fastapi import HTTPException, status
from ..repositories.savings_repository import SavingsRepository
from ..dtos.savings_dto import SavingsEnvelopeCreate, SavingsEnvelopeUpdate


class SavingsService:
    """
    Servicio de sobres de ahorro.
    Maneja la lógica de negocio para objetivos de ahorro.
    """
    
    def __init__(self, savings_repo: SavingsRepository):
        self.savings_repo = savings_repo
    
    def create_envelope(self, user_id: int, envelope_data: SavingsEnvelopeCreate) -> Dict[str, Any]:
        """
        Crea un nuevo sobre de ahorro.
        
        Args:
            user_id: ID del usuario
            envelope_data: Datos del sobre
            
        Returns:
            Dict con el sobre creado
        """
        envelope_dict = envelope_data.model_dump()
        envelope_dict['user_id'] = user_id
        
        return self.savings_repo.create(envelope_dict)
    
    def get_envelopes_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los sobres de ahorro de un usuario.
        Agrega el porcentaje de progreso a cada sobre.
        """
        envelopes = self.savings_repo.get_by_user(user_id)
        
        # Agregar porcentaje de progreso a cada sobre
        for envelope in envelopes:
            target = envelope.get('target_amount', 0.0)
            current = envelope.get('current_amount', 0.0)
            if target > 0:
                envelope['progress_percentage'] = (current / target) * 100
            else:
                envelope['progress_percentage'] = 0.0
        
        return envelopes
    
    def get_envelope_by_id(self, user_id: int, envelope_id: int) -> Dict[str, Any]:
        """
        Obtiene un sobre de ahorro específico.
        
        Args:
            user_id: ID del usuario
            envelope_id: ID del sobre
            
        Returns:
            Dict con el sobre
            
        Raises:
            HTTPException: Si el sobre no existe o no pertenece al usuario
        """
        envelope = self.savings_repo.get_by_id(envelope_id)
        
        if not envelope:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings envelope not found"
            )
        
        if envelope['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this savings envelope"
            )
        
        # Agregar porcentaje de progreso
        target = envelope.get('target_amount', 0.0)
        current = envelope.get('current_amount', 0.0)
        if target > 0:
            envelope['progress_percentage'] = (current / target) * 100
        else:
            envelope['progress_percentage'] = 0.0
        
        return envelope
    
    def update_envelope(
        self, 
        user_id: int, 
        envelope_id: int, 
        envelope_data: SavingsEnvelopeUpdate
    ) -> Dict[str, Any]:
        """
        Actualiza un sobre de ahorro existente.
        
        Args:
            user_id: ID del usuario
            envelope_id: ID del sobre
            envelope_data: Nuevos datos del sobre
            
        Returns:
            Dict con el sobre actualizado
        """
        # Verificar que el sobre existe y pertenece al usuario
        existing = self.get_envelope_by_id(user_id, envelope_id)
        
        # Actualizar solo los campos proporcionados
        update_dict = envelope_data.model_dump(exclude_unset=True)
        existing.update(update_dict)
        
        # Recalcular progreso
        target = existing.get('target_amount', 0.0)
        current = existing.get('current_amount', 0.0)
        if target > 0:
            existing['progress_percentage'] = (current / target) * 100
        else:
            existing['progress_percentage'] = 0.0
        
        return self.savings_repo.update(envelope_id, existing)
    
    def delete_envelope(self, user_id: int, envelope_id: int) -> bool:
        """
        Elimina un sobre de ahorro.
        
        Args:
            user_id: ID del usuario
            envelope_id: ID del sobre
            
        Returns:
            True si se eliminó correctamente
        """
        # Verificar que el sobre existe y pertenece al usuario
        self.get_envelope_by_id(user_id, envelope_id)
        
        return self.savings_repo.delete(envelope_id)
    
    def add_amount(self, user_id: int, envelope_id: int, amount: float) -> Dict[str, Any]:
        """
        Agrega dinero a un sobre de ahorro.
        
        Args:
            user_id: ID del usuario
            envelope_id: ID del sobre
            amount: Cantidad a agregar
            
        Returns:
            Dict con el sobre actualizado
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than zero"
            )
        
        envelope = self.get_envelope_by_id(user_id, envelope_id)
        envelope['current_amount'] = envelope.get('current_amount', 0.0) + amount
        
        return self.savings_repo.update(envelope_id, envelope)