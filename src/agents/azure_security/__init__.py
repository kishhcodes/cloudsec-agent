"""
Azure Security Agent Module

Provides comprehensive security assessment and analysis for Microsoft Azure.
"""

from .agent import AzureSecurityAgent
from .utils import (
    AzureSecurityPatterns,
    AzureRiskAssessment,
    AzureSecurityRecommendations,
    AzureComplianceFrameworks
)

__all__ = [
    'AzureSecurityAgent',
    'AzureSecurityPatterns',
    'AzureRiskAssessment',
    'AzureSecurityRecommendations',
    'AzureComplianceFrameworks'
]
