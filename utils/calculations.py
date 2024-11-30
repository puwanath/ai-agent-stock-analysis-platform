"""
Financial and Technical Analysis Calculations Module
Contains various calculation functions for financial analysis.
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import ta

class FinancialCalculations:
    """Financial calculations and metrics"""
    
    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """Calculate simple returns"""
        return prices.pct_change()

    @staticmethod
    def calculate_log_returns(prices: pd.Series) -> pd.Series:
        """Calculate logarithmic returns"""
        return np.log(prices / prices.shift(1))

    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 252) -> float:
        """Calculate annualized volatility"""
        return returns.std() * np.sqrt(window)

    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252
    ) -> float:
        """Calculate Sharpe Ratio"""
        excess_returns = returns - risk_free_rate/periods_per_year
        return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()

    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252
    ) -> float:
        """Calculate Sortino Ratio"""
        excess_returns = returns - risk_free_rate/periods_per_year
        downside_returns = returns[returns < 0]
        downside_std = np.sqrt(np.mean(downside_returns**2))
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std

    @staticmethod
    def calculate_max_drawdown(prices: pd.Series) -> float:
        """Calculate Maximum Drawdown"""
        rolling_max = prices.expanding().max()
        drawdowns = prices/rolling_max - 1
        return drawdowns.min()

    @staticmethod
    def calculate_beta(
        returns: pd.Series,
        market_returns: pd.Series
    ) -> float:
        """Calculate Beta relative to market"""
        covariance = returns.cov(market_returns)
        market_variance = market_returns.var()
        return covariance / market_variance

    @staticmethod
    def calculate_alpha(
        returns: pd.Series,
        market_returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """Calculate Alpha (Jensen's Alpha)"""
        beta = FinancialCalculations.calculate_beta(returns, market_returns)
        excess_return = returns.mean() * 252 - risk_free_rate
        market_excess_return = market_returns.mean() * 252 - risk_free_rate
        return excess_return - beta * market_excess_return

class TechnicalCalculations:
    """Technical analysis calculations"""
    
    @staticmethod
    def calculate_sma(prices: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: int = 2
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        middle_band = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        return {
            'upper': middle_band + (std * std_dev),
            'middle': middle_band,
            'lower': middle_band - (std * std_dev)
        }

    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """Calculate MACD"""
        fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_line = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d_line = k_line.rolling(window=d_period).mean()
        
        return {'k': k_line, 'd': d_line}

    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

class RiskCalculations:
    """Risk metrics calculations"""
    
    @staticmethod
    def calculate_var(
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)

    @staticmethod
    def calculate_cvar(
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = RiskCalculations.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()

    @staticmethod
    def calculate_downside_deviation(
        returns: pd.Series,
        target_return: float = 0
    ) -> float:
        """Calculate Downside Deviation"""
        downside_returns = returns[returns < target_return]
        return np.sqrt(np.mean(downside_returns**2))

    @staticmethod
    def calculate_risk_metrics(returns: pd.Series) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        return {
            'volatility': FinancialCalculations.calculate_volatility(returns),
            'var_95': RiskCalculations.calculate_var(returns),
            'cvar_95': RiskCalculations.calculate_cvar(returns),
            'max_drawdown': FinancialCalculations.calculate_max_drawdown(returns),
            'downside_deviation': RiskCalculations.calculate_downside_deviation(returns)
        }

class VolumeCalculations:
    """Volume analysis calculations"""
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        return (np.sign(close.diff()) * volume).cumsum()

    @staticmethod
    def calculate_vwap(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        return (typical_price * volume).cumsum() / volume.cumsum()

    @staticmethod
    def calculate_mfi(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """Calculate Money Flow Index"""
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        return mfi

def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all technical indicators for a DataFrame"""
    df = df.copy()
    
    # Moving Averages
    for period in [20, 50, 200]:
        df[f'SMA_{period}'] = TechnicalCalculations.calculate_sma(df['Close'], period)
    
    # Bollinger Bands
    bb = TechnicalCalculations.calculate_bollinger_bands(df['Close'])
    df['BB_upper'] = bb['upper']
    df['BB_middle'] = bb['middle']
    df['BB_lower'] = bb['lower']
    
    # MACD
    macd = TechnicalCalculations.calculate_macd(df['Close'])
    df['MACD'] = macd['macd']
    df['MACD_signal'] = macd['signal']
    df['MACD_hist'] = macd['histogram']
    
    # RSI
    df['RSI'] = TechnicalCalculations.calculate_rsi(df['Close'])
    
    # Stochastic
    stoch = TechnicalCalculations.calculate_stochastic(df['High'], df['Low'], df['Close'])
    df['Stoch_K'] = stoch['k']
    df['Stoch_D'] = stoch['d']
    
    # ATR
    df['ATR'] = TechnicalCalculations.calculate_atr(df['High'], df['Low'], df['Close'])
    
    # Volume Indicators
    df['OBV'] = VolumeCalculations.calculate_obv(df['Close'], df['Volume'])
    df['VWAP'] = VolumeCalculations.calculate_vwap(df['High'], df['Low'], 
                                                  df['Close'], df['Volume'])
    df['MFI'] = VolumeCalculations.calculate_mfi(df['High'], df['Low'], 
                                                df['Close'], df['Volume'])
    
    return df