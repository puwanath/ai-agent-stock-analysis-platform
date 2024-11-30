"""
Stock Analysis Components Module
"""

# Version information
__version__ = '1.0.0'

# Import only existing functions
from .technical import TechnicalAnalysis, display_technical_analysis
from .company_info import display_company_info
from .financial import display_financial_metrics  # Removed display_financial_ratios
from .news import display_news_section
from .risk import display_risk_metrics, display_trading_signals
from .charts import display_chart_analysis, ChartCreator
from .research import display_research_analysis

# Component configuration
DEFAULT_CONFIG = {
    'theme': 'plotly_dark',
    'chart_height': 800,
    'show_volume': True,
    'show_indicators': True,
    'max_news_items': 5,
    'time_periods': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
}

# Export what we want to make available
__all__ = [
    'TechnicalAnalysis',
    'display_technical_analysis',
    'display_company_info',
    'display_financial_metrics', 
    'display_news_section',
    'display_risk_metrics',
    'display_trading_signals',
    'display_chart_analysis',
    'display_research_analysis',   
    'ChartCreator',
    'DEFAULT_CONFIG'
]