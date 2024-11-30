"""
Technical Indicators Utility Module
"""

import pandas as pd
import numpy as np
import ta

def get_technical_indicators(df: pd.DataFrame) -> dict:
    """
    Calculate technical indicators from price data
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Dictionary with technical indicators and their interpretations
    """
    indicators = {}
    
    try:
        # Get latest values
        latest_close = df['Close'].iloc[-1]
        
        # Moving Averages
        ma_periods = [20, 50, 200]
        for period in ma_periods:
            df[f'MA{period}'] = ta.trend.sma_indicator(df['Close'], window=period)
            indicators[f'MA{period}'] = df[f'MA{period}'].iloc[-1]
        
        # MA Signals
        ma_signals = []
        if latest_close > indicators['MA50']:
            ma_signals.append("Price above 50-day MA (Bullish)")
        else:
            ma_signals.append("Price below 50-day MA (Bearish)")
            
        if indicators['MA50'] > indicators['MA200']:
            ma_signals.append("Golden Cross pattern (Bullish)")
        elif indicators['MA50'] < indicators['MA200']:
            ma_signals.append("Death Cross pattern (Bearish)")
            
        indicators['MA_Status'] = '; '.join(ma_signals)
        
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        rsi_value = df['RSI'].iloc[-1]
        indicators['RSI'] = rsi_value
        
        if rsi_value > 70:
            indicators['RSI_Signal'] = "Overbought"
        elif rsi_value < 30:
            indicators['RSI_Signal'] = "Oversold"
        else:
            indicators['RSI_Signal'] = "Neutral"
        
        # MACD
        df['MACD'] = ta.trend.macd_diff(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
        
        macd_value = df['MACD'].iloc[-1]
        macd_signal = df['MACD_Signal'].iloc[-1]
        indicators['MACD'] = macd_value
        
        if macd_value > macd_signal:
            indicators['MACD_Signal'] = "Bullish"
        else:
            indicators['MACD_Signal'] = "Bearish"
        
        # Bollinger Bands
        df['BB_upper'] = ta.volatility.bollinger_hband(df['Close'])
        df['BB_middle'] = ta.volatility.bollinger_mavg(df['Close'])
        df['BB_lower'] = ta.volatility.bollinger_lband(df['Close'])
        
        bb_upper = df['BB_upper'].iloc[-1]
        bb_lower = df['BB_lower'].iloc[-1]
        
        if latest_close > bb_upper:
            indicators['BB_Status'] = "Price above upper band (Overbought)"
        elif latest_close < bb_lower:
            indicators['BB_Status'] = "Price below lower band (Oversold)"
        else:
            indicators['BB_Status'] = "Price within bands (Neutral)"
            
        # Volume Analysis
        avg_volume = df['Volume'].mean()
        current_volume = df['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 2:
            indicators['Volume_Signal'] = "Unusually high volume"
        elif volume_ratio < 0.5:
            indicators['Volume_Signal'] = "Unusually low volume"
        else:
            indicators['Volume_Signal'] = "Normal volume"
            
        # Trend Analysis
        short_term_trend = (latest_close - df['Close'].iloc[-5]) / df['Close'].iloc[-5] * 100
        medium_term_trend = (latest_close - df['Close'].iloc[-20]) / df['Close'].iloc[-20] * 100
        
        indicators['Short_Term_Trend'] = f"{short_term_trend:.1f}% {'up' if short_term_trend > 0 else 'down'}"
        indicators['Medium_Term_Trend'] = f"{medium_term_trend:.1f}% {'up' if medium_term_trend > 0 else 'down'}"
        
        # Overall Signal
        bullish_signals = sum([
            latest_close > indicators['MA50'],
            indicators['MA50'] > indicators['MA200'],
            30 <= rsi_value <= 70,
            macd_value > macd_signal,
            volume_ratio > 1
        ])
        
        bearish_signals = sum([
            latest_close < indicators['MA50'],
            indicators['MA50'] < indicators['MA200'],
            rsi_value > 70 or rsi_value < 30,
            macd_value < macd_signal,
            volume_ratio < 1
        ])
        
        if bullish_signals > bearish_signals:
            indicators['Overall_Signal'] = "Bullish"
        elif bearish_signals > bullish_signals:
            indicators['Overall_Signal'] = "Bearish"
        else:
            indicators['Overall_Signal'] = "Neutral"
            
        # Support and Resistance
        recent_high = df['High'].rolling(window=20).max().iloc[-1]
        recent_low = df['Low'].rolling(window=20).min().iloc[-1]
        
        indicators['Support_Level'] = recent_low
        indicators['Resistance_Level'] = recent_high
        
        # Volatility
        volatility = df['Close'].pct_change().std() * np.sqrt(252) * 100
        indicators['Volatility'] = f"{volatility:.1f}%"
        
        return indicators
        
    except Exception as e:
        print(f"Error calculating technical indicators: {e}")
        return {
            'error': str(e),
            'MA_Status': 'N/A',
            'RSI': 'N/A',
            'MACD': 'N/A',
            'BB_Status': 'N/A',
            'Overall_Signal': 'N/A'
        }

def interpret_indicators(indicators: dict) -> str:
    """
    Generate human-readable interpretation of technical indicators
    
    Args:
        indicators: Dictionary of technical indicators
        
    Returns:
        String with interpretation
    """
    interpretation = []
    
    # Moving Averages
    interpretation.append(f"Moving Averages: {indicators.get('MA_Status', 'N/A')}")
    
    # RSI
    rsi = indicators.get('RSI', 0)
    rsi_signal = indicators.get('RSI_Signal', 'N/A')
    interpretation.append(f"RSI is at {rsi:.1f} indicating {rsi_signal} conditions")
    
    # MACD
    interpretation.append(f"MACD shows {indicators.get('MACD_Signal', 'N/A')} momentum")
    
    # Bollinger Bands
    interpretation.append(f"Bollinger Bands: {indicators.get('BB_Status', 'N/A')}")
    
    # Volume
    interpretation.append(f"Volume Analysis: {indicators.get('Volume_Signal', 'N/A')}")
    
    # Trends
    interpretation.append(f"Short-term trend: {indicators.get('Short_Term_Trend', 'N/A')}")
    interpretation.append(f"Medium-term trend: {indicators.get('Medium_Term_Trend', 'N/A')}")
    
    # Volatility
    interpretation.append(f"Current volatility: {indicators.get('Volatility', 'N/A')}")
    
    # Overall Signal
    interpretation.append(f"Overall Technical Signal: {indicators.get('Overall_Signal', 'N/A')}")
    
    return "\n".join(interpretation)