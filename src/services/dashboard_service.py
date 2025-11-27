from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from ..repositories.transaction_repository import TransactionRepository
from ..repositories.card_repository import CardRepository
from ..repositories.savings_repository import SavingsRepository
from ..repositories.reminder_repository import ReminderRepository
from ..dtos.dashboard_dto import DashboardSummary, CategorySummary


class DashboardService:
    """
    Servicio de dashboard.
    Maneja la lógica de negocio para el resumen financiero del usuario.
    """
    
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        card_repo: CardRepository,
        savings_repo: SavingsRepository,
        reminder_repo: ReminderRepository
    ):
        self.transaction_repo = transaction_repo
        self.card_repo = card_repo
        self.savings_repo = savings_repo
        self.reminder_repo = reminder_repo
    
    def get_dashboard_summary(
        self, 
        user_id: int, 
        days: int = 30
    ) -> DashboardSummary:
        """
        Obtiene el resumen completo del dashboard para un usuario.
        
        Args:
            user_id: ID del usuario
            days: Número de días hacia atrás para el análisis (default: 30)
            
        Returns:
            DashboardSummary con todos los datos del dashboard
        """
        # Definir el rango de fechas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Obtener transacciones del periodo
        transactions = self.transaction_repo.get_by_user_and_date_range(
            user_id, start_date, end_date
        )
        
        # Calcular totales de ingresos y gastos
        total_income = 0.0
        total_expenses = 0.0
        
        # Agrupar por categoría
        expenses_by_category = defaultdict(lambda: {'total_amount': 0.0, 'count': 0})
        income_by_category = defaultdict(lambda: {'total_amount': 0.0, 'count': 0})
        
        for transaction in transactions:
            amount = transaction.get('amount', 0.0)
            category = transaction.get('category', 'Other')
            transaction_type = transaction.get('transaction_type', '')
            
            if transaction_type == 'income':
                total_income += amount
                income_by_category[category]['total_amount'] += amount
                income_by_category[category]['count'] += 1
            elif transaction_type == 'expense':
                total_expenses += amount
                expenses_by_category[category]['total_amount'] += amount
                expenses_by_category[category]['count'] += 1
        
        # Convertir a listas de CategorySummary
        expenses_list = [
            CategorySummary(
                category=cat,
                total_amount=data['total_amount'],
                transaction_count=data['count']
            )
            for cat, data in sorted(
                expenses_by_category.items(),
                key=lambda x: x[1]['total_amount'],
                reverse=True
            )
        ]
        
        income_list = [
            CategorySummary(
                category=cat,
                total_amount=data['total_amount'],
                transaction_count=data['count']
            )
            for cat, data in sorted(
                income_by_category.items(),
                key=lambda x: x[1]['total_amount'],
                reverse=True
            )
        ]
        
        # Datos de tarjetas
        total_cards = len(self.card_repo.get_by_user(user_id))
        total_cards_balance = self.card_repo.get_total_balance_by_user(user_id)
        
        # Datos de sobres de ahorro
        total_savings = self.savings_repo.get_total_savings_by_user(user_id)
        savings_progress = self.savings_repo.get_average_progress_by_user(user_id)
        
        # Datos de recordatorios
        pending_reminders = len(self.reminder_repo.get_pending_by_user(user_id))
        overdue_reminders = len(self.reminder_repo.get_overdue_by_user(user_id))
        
        # Balance general
        balance = total_income - total_expenses
        
        return DashboardSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            balance=balance,
            total_cards=total_cards,
            total_cards_balance=total_cards_balance,
            total_savings=total_savings,
            savings_progress=savings_progress,
            pending_reminders=pending_reminders,
            overdue_reminders=overdue_reminders,
            expenses_by_category=expenses_list,
            income_by_category=income_list,
            recent_transactions_count=len(transactions),
            period_start=start_date,
            period_end=end_date
        )
    
    def get_category_breakdown(self, user_id: int, transaction_type: str) -> List[CategorySummary]:
        """
        Obtiene el desglose por categorías de un tipo de transacción específico.
        
        Args:
            user_id: ID del usuario
            transaction_type: Tipo de transacción ('income' o 'expense')
            
        Returns:
            Lista de CategorySummary ordenada por monto
        """
        transactions = self.transaction_repo.get_by_user_and_type(user_id, transaction_type)
        
        category_data = defaultdict(lambda: {'total_amount': 0.0, 'count': 0})
        
        for transaction in transactions:
            amount = transaction.get('amount', 0.0)
            category = transaction.get('category', 'Other')
            category_data[category]['total_amount'] += amount
            category_data[category]['count'] += 1
        
        return [
            CategorySummary(
                category=cat,
                total_amount=data['total_amount'],
                transaction_count=data['count']
            )
            for cat, data in sorted(
                category_data.items(),
                key=lambda x: x[1]['total_amount'],
                reverse=True
            )
        ]