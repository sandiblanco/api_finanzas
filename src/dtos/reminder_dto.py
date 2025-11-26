from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..utils.enums import PriorityLevel


class PaymentReminderBase(BaseModel):
    """Schema base para recordatorio de pago"""
    payment_name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    due_date: datetime
    category: str = Field(..., min_length=1, max_length=100)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    is_paid: bool = Field(default=False)
    description: Optional[str] = Field(None, max_length=500)


class PaymentReminderCreate(PaymentReminderBase):
    """Schema para crear recordatorio de pago"""
    pass


class PaymentReminderUpdate(BaseModel):
    """Schema para actualizar recordatorio de pago"""
    payment_name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    priority: Optional[PriorityLevel] = None
    is_paid: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)


class PaymentReminderResponse(PaymentReminderBase):
    """Schema para respuesta de recordatorio de pago"""
    id: int
    user_id: int
    is_overdue: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentReminderListResponse(BaseModel):
    """Schema para lista de recordatorios de pago"""
    total: int
    reminders: list[PaymentReminderResponse]