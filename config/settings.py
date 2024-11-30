"""
Settings Configuration Module
Contains all configuration settings for the stock analysis platform
"""

import os
from datetime import datetime
from typing import Dict, Any

# Application Metadata
APP_METADATA = {
    "name": "AI-Agents Finance Analyst Platform",
    "version": "1.0.0",
    "author": "AI-Agents Finance Team",
    "description": "Advanced stock analysis and visualization platform",
    "last_updated": datetime.now().strftime("%Y-%m-%d")
}

# Streamlit Application Settings
STREAMLIT_CONFIG = {
    "page": {
        "title": "AI-Agents Finance Analyst Platform",
        "icon": "📈",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
        "menu_items": {
            "About": "Advanced Stock Analysis Platform",
            "Get help": "https://github.com/yourusername/stockanalysis",
            "Report a bug": "https://github.com/yourusername/stockanalysis/issues"
        }
    },
    "theme": {
        "primaryColor": "#1f77b4",
        "backgroundColor": "#0e1117",
        "secondaryBackgroundColor": "#262730",
        "textColor": "#fafafa",
        "font": "sans serif"
    }
}

# Data Settings
DATA_CONFIG = {
    "yahoo_finance": {
        "request_timeout": 30,
        "max_retries": 3,
        "retry_delay": 5
    },
    "default_timeframes": {
        "intraday": ["1m", "5m", "15m", "30m", "1h"],
        "daily": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        "default": "1y"
    },
    "cache": {
        "enabled": True,
        "expiry": 3600,  # 1 hour in seconds
        "max_size": 1000  # Maximum items in cache
    }
}

# Technical Analysis Settings
TECHNICAL_ANALYSIS = {
    "moving_averages": {
        "sma_periods": [20, 50, 200],
        "ema_periods": [9, 21, 55],
        "default_ma_type": "SMA"
    },
    "oscillators": {
        "rsi": {
            "period": 14,
            "overbought": 70,
            "oversold": 30
        },
        "macd": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        },
        "stochastic": {
            "k_period": 14,
            "d_period": 3,
            "overbought": 80,
            "oversold": 20
        }
    },
    "volatility": {
        "bollinger_bands": {
            "period": 20,
            "std_dev": 2
        },
        "atr": {
            "period": 14
        },
        "keltner_channels": {
            "period": 20,
            "atr_multiplier": 2
        }
    },
    "volume": {
        "vwap": {
            "period": "day"
        },
        "obv": {
            "signal_period": 21
        },
        "mfi": {
            "period": 14,
            "overbought": 80,
            "oversold": 20
        }
    },
    "support_resistance": {
        "pivot_points": {
            "method": "traditional",  # or fibonacci
            "levels": ["S2", "S1", "P", "R1", "R2"]
        },
        "price_levels": {
            "lookback_period": 90,
            "threshold": 0.02  # 2% tolerance
        }
    }
}

# Chart Settings
CHART_CONFIG = {
    "general": {
        "theme": "plotly_dark",
        "default_height": 800,
        "show_volume": True,
        "show_indicators": True
    },
    "colors": {
        "up": "#26a69a",      # Green for upward movement
        "down": "#ef5350",    # Red for downward movement
        "volume_up": "#26a69a",
        "volume_down": "#ef5350",
        "ma_lines": ["#1f77b4", "#ff7f0e", "#2ca02c"],
        "bb_bands": ["#7570b3", "#7570b3", "#7570b3"]
    },
    "layout": {
        "margin": {"l": 50, "r": 50, "t": 50, "b": 50},
        "showlegend": True,
        "xaxis_rangeslider_visible": False
    }
}

# Financial Analysis Settings
FINANCIAL_ANALYSIS = {
    "metrics": {
        "risk_free_rate": 0.02,  # 2% annual risk-free rate
        "market_benchmark": "SPY",
        "time_periods": ["1y", "3y", "5y", "10y"],
        "min_data_points": 252  # Minimum data points for analysis
    },
    "ratios": {
        "valuation": ["P/E", "P/B", "P/S", "EV/EBITDA"],
        "profitability": ["ROE", "ROA", "Profit Margin"],
        "liquidity": ["Current Ratio", "Quick Ratio"],
        "efficiency": ["Asset Turnover", "Inventory Turnover"]
    },
    "growth": {
        "periods": ["QoQ", "YoY", "3Y", "5Y"],
        "metrics": ["Revenue", "EPS", "EBITDA"]
    }
}

# Risk Analysis Settings
RISK_ANALYSIS = {
    "metrics": {
        "var_confidence_levels": [0.95, 0.99],
        "volatility_window": 252,
        "beta_benchmark": "SPY",
        "risk_levels": {
            "low": 0.15,      # 15% annual volatility
            "medium": 0.25,   # 25% annual volatility
            "high": 0.35      # 35% annual volatility
        }
    },
    "stress_test": {
        "scenarios": ["2008 Crisis", "2020 Covid", "2022 Bear Market"],
        "custom_scenarios": True,
        "max_drawdown_periods": [21, 63, 252]  # Days
    }
}

# News Analysis Settings
NEWS_ANALYSIS = {
    "sources": {
        "yahoo_finance": True,
        "seeking_alpha": False,
        "bloomberg": False
    },
    "filters": {
        "max_age": 30,  # Days
        "relevance_threshold": 0.5,
        "max_articles": 50
    },
    "sentiment": {
        "analyze": True,
        "thresholds": {
            "positive": 0.1,
            "negative": -0.1
        }
    }
}

# Error Messages
ERROR_MESSAGES = {
    "data": {
        "fetch_error": "Error fetching data. Please try again.",
        "invalid_symbol": "Invalid stock symbol. Please enter a valid symbol.",
        "no_data": "No data available for the selected period.",
        "calculation_error": "Error in calculations. Please check input data."
    },
    "technical": {
        "indicator_error": "Error calculating technical indicator.",
        "insufficient_data": "Insufficient data for technical analysis."
    },
    "financial": {
        "ratio_error": "Error calculating financial ratios.",
        "missing_data": "Missing required financial data."
    }
}

# AI Analysis Settings
AI_CONFIG = {
    'ai_analysis': {
        'enabled': True,  # Set to False to disable AI analysis
        'api_url': 'http://localhost:11434/api/generate',
        'model': 'mistral',  # or other models supported by Ollama
        'timeout': 30,
        'cache_duration': 3600,  # Cache AI analysis for 1 hour
        'min_confidence': 0.7,  # Minimum confidence level for recommendations
    }
}

class Settings:
    """Settings management class"""
    def __init__(self):
        self.config = {
            "data": {
                "available_symbols": [
                    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
                    "TSLA", "NVDA", "JPM", "V", "WMT"
                ],
                "default_timeframes": {
                    "daily": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
                }
            }
        }

    def get_all_settings(self):
        return self.config
    
    # @staticmethod
    # def get_all_settings() -> Dict[str, Any]:
    #     """Get all settings as a dictionary"""
    #     return {
    #         "app_metadata": APP_METADATA,
    #         "streamlit": STREAMLIT_CONFIG,
    #         "data": DATA_CONFIG,
    #         "technical": TECHNICAL_ANALYSIS,
    #         "chart": CHART_CONFIG,
    #         "financial": FINANCIAL_ANALYSIS,
    #         "risk": RISK_ANALYSIS,
    #         "news": NEWS_ANALYSIS,
    #         "errors": ERROR_MESSAGES
    #     }
    
    @staticmethod
    def get_streamlit_config() -> Dict[str, Any]:
        """Get Streamlit specific configuration"""
        return STREAMLIT_CONFIG
    
    @staticmethod
    def get_technical_settings() -> Dict[str, Any]:
        """Get technical analysis settings"""
        return TECHNICAL_ANALYSIS
    
    @staticmethod
    def get_chart_settings() -> Dict[str, Any]:
        """Get chart settings"""
        return CHART_CONFIG
    
    @staticmethod
    def get_error_message(category: str, key: str) -> str:
        """Get specific error message"""
        return ERROR_MESSAGES.get(category, {}).get(key, "An unknown error occurred.")

# Environment-specific settings
ENV = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Export settings
__all__ = [
    'Settings',
    'APP_METADATA',
    'STREAMLIT_CONFIG',
    'DATA_CONFIG',
    'TECHNICAL_ANALYSIS',
    'CHART_CONFIG',
    'FINANCIAL_ANALYSIS',
    'RISK_ANALYSIS',
    'NEWS_ANALYSIS',
    'ERROR_MESSAGES',
    'ENV',
    'DEBUG'
]