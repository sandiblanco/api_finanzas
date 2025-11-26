from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SavingsEnvelopeBase(BaseModel):
    """Schema base para sobre de ahorro"""
    name: str = Field(..., min_length=1, max_length=100)
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    description: Optional[str] = Field(None, max_length=500)


class SavingsEnvelopeCreate(SavingsEnvelopeBase):
    """Schema para crear sobre de ahorro"""
    pass


class SavingsEnvelopeUpdate(BaseModel):
    """Schema para actualizar sobre de ahorro"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)


class SavingsEnvelopeResponse(SavingsEnvelopeBase):
    """Schema para respuesta de sobre de ahorro"""
    id: int
    user_id: int
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SavingsEnvelopeListResponse(BaseModel):
    """Schema para lista de sobres de ahorro"""
    total: int
    envelopes: list[SavingsEnvelopeResponse]