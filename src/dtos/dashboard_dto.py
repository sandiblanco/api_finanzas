from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime


class CategorySummary(BaseModel):
    """Resumen por categoría"""
    category: str
    total_amount: float
    transaction_count: int


class DashboardSummary(BaseModel):
    """Schema para resumen del dashboard"""
    total_income: float
    total_expenses: float
    balance: float
    total_cards: int
    total_cards_balance: float
    total_savings: float
    savings_progress: float
    pending_reminders: int
    overdue_reminders: int
    
    # Desglose por categorías
    expenses_by_category: List[CategorySummary]
    income_by_category: List[CategorySummary]
    
    # Últimas transacciones
    recent_transactions_count: int
    
    # Periodo del resumen
    period_start: datetime
    period_end: datetime


class MonthlyComparison(BaseModel):
    """Comparación mensual"""
    current_month_income: float
    current_month_expenses: float
    previous_month_income: float
    previous_month_expenses: float
    income_change_percentage: float
    expenses_change_percentage: float