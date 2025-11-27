from fastapi import APIRouter, Depends, Query
from typing import Dict, Any
from ..services.dashboard_service import DashboardService
from ..repositories.transaction_repository import TransactionRepository
from ..repositories.card_repository import CardRepository
from ..repositories.savings_repository import SavingsRepository
from ..repositories.reminder_repository import ReminderRepository
from ..dtos.dashboard_dto import DashboardSummary
from ..config.json_db import get_db, JSONDatabase
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service(db: JSONDatabase = Depends(get_db)) -> DashboardService:
    """Dependency para obtener el servicio de dashboard"""
    transaction_repo = TransactionRepository(db)
    card_repo = CardRepository(db)
    savings_repo = SavingsRepository(db)
    reminder_repo = ReminderRepository(db)
    return DashboardService(transaction_repo, card_repo, savings_repo, reminder_repo)


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    days: int = Query(default=30, ge=1, le=365,
                      description="Número de días hacia atrás para el análisis"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Obtiene el resumen completo del dashboard financiero del usuario.

    Incluye:
    - Total de ingresos y gastos en el periodo
    - Balance actual
    - Información de tarjetas y su balance total
    - Progreso de ahorro
    - Recordatorios pendientes y vencidos
    - Desglose por categorías de ingresos y gastos

    **Parámetros:**
    - **days**: Número de días hacia atrás para el análisis (por defecto 30, máximo 365)
    """
    user_id = current_user['id']
    return dashboard_service.get_dashboard_summary(user_id, days)
