from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..utils.enums import TransactionType, PaymentMethod


class TransactionBase(BaseModel):
    """Schema base para transacción"""
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    amount: float = Field(..., gt=0)
    transaction_type: TransactionType
    payment_method: PaymentMethod
    card_id: Optional[int] = None
    transaction_date: Optional[datetime] = None


class TransactionCreate(TransactionBase):
    """Schema para crear transacción"""
    pass


class TransactionUpdate(BaseModel):
    """Schema para actualizar transacción"""
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[TransactionType] = None
    payment_method: Optional[PaymentMethod] = None
    card_id: Optional[int] = None
    transaction_date: Optional[datetime] = None


class TransactionResponse(TransactionBase):
    """Schema para respuesta de transacción"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema para lista de transacciones"""
    total: int
    transactions: list[TransactionResponse]