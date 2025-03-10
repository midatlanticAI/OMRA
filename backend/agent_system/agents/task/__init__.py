"""
Task Agents package for OpenManus Appliance Repair Business Automation System
"""

from .base_task_agent import TaskAgent
from .communication_agent import CommunicationAgent
from .customer_history_agent import CustomerHistoryAgent
from .satisfaction_analysis_agent import SatisfactionAnalysisAgent

__all__ = [
    'TaskAgent',
    'CommunicationAgent',
    'CustomerHistoryAgent',
    'SatisfactionAnalysisAgent'
] 