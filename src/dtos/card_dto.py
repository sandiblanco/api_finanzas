from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CardBase(BaseModel):
    """Schema base para tarjeta"""
    bank_name: str = Field(..., min_length=1, max_length=100)
    card_type: str = Field(..., min_length=1, max_length=50)
    last_four_digits: str = Field(..., min_length=4, max_length=4, pattern=r'^\d{4}$')
    balance: float = Field(default=0.0, ge=0)
    card_holder_name: Optional[str] = Field(None, max_length=100)


class CardCreate(CardBase):
    """Schema para crear tarjeta"""
    pass


class CardUpdate(BaseModel):
    """Schema para actualizar tarjeta"""
    bank_name: Optional[str] = Field(None, min_length=1, max_length=100)
    card_type: Optional[str] = Field(None, min_length=1, max_length=50)
    last_four_digits: Optional[str] = Field(None, min_length=4, max_length=4, pattern=r'^\d{4}$')
    balance: Optional[float] = Field(None, ge=0)
    card_holder_name: Optional[str] = Field(None, max_length=100)


class CardResponse(CardBase):
    """Schema para respuesta de tarjeta"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CardListResponse(BaseModel):
    """Schema para lista de tarjetas"""
    total: int
    cards: list[CardResponse]