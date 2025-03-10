"""
Manager Agents package for OpenManus Appliance Repair Business Automation System
"""

from .base_manager_agent import ManagerAgent
from .customer_relations_agent import CustomerRelationsAgent
from .service_operations_agent import ServiceOperationsAgent
from .financial_operations_agent import FinancialOperationsAgent
from .marketing_agent import MarketingAgent
from .administrative_agent import AdministrativeAgent

__all__ = [
    'ManagerAgent',
    'CustomerRelationsAgent',
    'ServiceOperationsAgent',
    'FinancialOperationsAgent',
    'MarketingAgent',
    'AdministrativeAgent'
] 