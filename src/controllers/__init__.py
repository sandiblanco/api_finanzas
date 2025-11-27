from .auth_controller import router as auth_router
from .transaction_controller import router as transaction_router
from .card_controller import router as card_router
from .savings_controller import router as savings_router
from .reminder_controller import router as reminder_router
from .dashboard_controller import router as dashboard_router

__all__ = [
    "auth_router",
    "transaction_router",
    "card_router",
    "savings_router",
    "reminder_router",
    "dashboard_router"
]