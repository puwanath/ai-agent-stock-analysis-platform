"""
Configuration Module for Stock Analysis Platform
This module manages all configuration settings for the application.
"""

import os
from datetime import datetime

# Application Version
__version__ = '1.0.0'
__author__ = 'AI-Agents Finance Team'

# Application Settings
APP_CONFIG = {
    "page_title": "AI-Agents Finance Analyst Platform",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Theme Configuration
THEME_CONFIG = {
    "primary_color": "#1f77b4",
    "background_color": "#0e1117",
    "secondary_background_color": "#262730",
    "text_color": "#fafafa",
    "font": "sans serif"
}

# Chart Settings
CHART_CONFIG = {
    "theme": "plotly_dark",
    "default_height": 800,
    "candlestick_colors": {
        "up": "#26a69a",      # Green for upward movement
        "down": "#ef5350",    # Red for downward movement
        "volume_up": "#26a69a",
        "volume_down": "#ef5350"
    }
}

# Technical Analysis Settings
TECHNICAL_INDICATORS = {
    "moving_averages": {
        "sma_periods": [20, 50, 200],
        "ema_periods": [9, 21, 55],
    },
    "oscillators": {
        "rsi_period": 14,
        "rsi_overbought": 70,
        "rsi_oversold": 30,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "stoch_k_period": 14,
        "stoch_d_period": 3
    },
    "volatility": {
        "bb_period": 20,
        "bb_std": 2,
        "atr_period": 14
    },
    "volume": {
        "vwap_period": 14,
        "mfi_period": 14
    }
}

# Financial Analysis Settings
FINANCIAL_METRICS = {
    "risk_free_rate": 0.02,  # 2% risk-free rate
    "market_benchmark": "SPY",  # S&P 500 ETF as benchmark
    "time_periods": ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    "default_period": "1y"
}

# Risk Analysis Settings
RISK_METRICS = {
    "volatility_window": 252,  # Trading days in a year
    "var_confidence_level": 0.95,
    "high_risk_threshold": 0.25,  # 25% annual volatility
    "moderate_risk_threshold": 0.15  # 15% annual volatility
}

# News Analysis Settings
NEWS_CONFIG = {
    "max_news_items": 10,
    "news_sources": ["yahoo", "seeking_alpha", "bloomberg"],
    "sentiment_thresholds": {
        "positive": 0.1,
        "negative": -0.1
    }
}

# API Settings
API_CONFIG = {
    "yahoo_finance": {
        "request_timeout": 30,
        "max_retries": 3,
        "retry_delay": 5
    }
}

# Cache Settings
CACHE_CONFIG = {
    "enable_cache": True,
    "cache_duration": 3600,  # 1 hour in seconds
    "max_cache_size": 1000  # Maximum number of items to cache
}

# Error Messages
ERROR_MESSAGES = {
    "data_fetch_error": "Error fetching data. Please try again.",
    "calculation_error": "Error in calculations. Please check input data.",
    "invalid_symbol": "Invalid stock symbol. Please enter a valid symbol.",
    "no_data_available": "No data available for the selected period."
}

def get_config():
    """Get complete configuration dictionary"""
    return {
        "app": APP_CONFIG,
        "theme": THEME_CONFIG,
        "chart": CHART_CONFIG,
        "technical": TECHNICAL_INDICATORS,
        "financial": FINANCIAL_METRICS,
        "risk": RISK_METRICS,
        "news": NEWS_CONFIG,
        "api": API_CONFIG,
        "cache": CACHE_CONFIG,
        "errors": ERROR_MESSAGES
    }

def get_app_config():
    """Get application configuration"""
    return APP_CONFIG

def get_chart_config():
    """Get chart configuration"""
    return CHART_CONFIG

def get_technical_config():
    """Get technical analysis configuration"""
    return TECHNICAL_INDICATORS

def get_risk_config():
    """Get risk analysis configuration"""
    return RISK_METRICS

def get_news_config():
    """Get news analysis configuration"""
    return NEWS_CONFIG

def get_error_message(key):
    """Get specific error message"""
    return ERROR_MESSAGES.get(key, "An unknown error occurred.")

class ConfigurationError(Exception):
    """Base exception for configuration-related errors"""
    pass

def validate_config():
    """Validate configuration settings"""
    required_settings = [
        ("APP_CONFIG", APP_CONFIG),
        ("CHART_CONFIG", CHART_CONFIG),
        ("TECHNICAL_INDICATORS", TECHNICAL_INDICATORS),
        ("FINANCIAL_METRICS", FINANCIAL_METRICS),
        ("RISK_METRICS", RISK_METRICS)
    ]
    
    missing_settings = []
    for setting_name, setting_value in required_settings:
        if not setting_value:
            missing_settings.append(setting_name)
            
    if missing_settings:
        raise ConfigurationError(
            f"Missing required configuration settings: {', '.join(missing_settings)}"
        )
    
    return True

def get_environment():
    """Get current environment settings"""
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "version": __version__,
        "timestamp": datetime.now().isoformat()
    }

# Initialize configuration on module import
try:
    validate_config()
except ConfigurationError as e:
    print(f"Configuration Error: {e}")
    raise

# Export all configurations
__all__ = [
    'get_config',
    'get_app_config',
    'get_chart_config',
    'get_technical_config',
    'get_risk_config',
    'get_news_config',
    'get_error_message',
    'get_environment',
    'validate_config',
    'ConfigurationError'
]