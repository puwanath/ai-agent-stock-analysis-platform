import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
import yfinance as yf
from datetime import datetime, timedelta

class TechnicalAnalysis:
    def __init__(self, df):
        """Initialize with DataFrame containing OHLCV data"""
        self.df = df.copy()
        self.current_price = df['Close'].iloc[-1]
        self.indicators = {}
        self.signals = {
            'bullish': [],
            'bearish': [],
            'neutral': []
        }
        
    def calculate_all_indicators(self):
        """Calculate all technical indicators"""
        self._calculate_moving_averages()
        self._calculate_momentum_indicators()
        self._calculate_trend_indicators()
        self._calculate_volatility_indicators()
        self._calculate_volume_indicators()
        self._calculate_support_resistance()
        return self.indicators
    
    def calculate_technical_indicators(df):
        # Replace infinite values with NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Add handling for zero values in denominator
        df['volume'] = df['Volume'].replace(0, np.nan)
        
        # Calculate indicators with proper error handling
        indicators = ta.trend.MACD(df['Close'])
        
        # Fill NaN values with forward fill method
        df = df.fillna(method='ffill')
        
        return df
        
    def _calculate_moving_averages(self):
        """Calculate various moving averages"""
        # Simple Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            self.df[f'SMA_{period}'] = ta.trend.sma_indicator(self.df['Close'], period)
            
        # Exponential Moving Averages
        for period in [9, 12, 26, 50]:
            self.df[f'EMA_{period}'] = ta.trend.ema_indicator(self.df['Close'], period)
            
        # MACD
        self.df['MACD_line'] = ta.trend.macd(self.df['Close'])
        self.df['MACD_signal'] = ta.trend.macd_signal(self.df['Close'])
        self.df['MACD_hist'] = ta.trend.macd_diff(self.df['Close'])
        
    def _calculate_momentum_indicators(self):
        """Calculate momentum indicators"""
        # RSI
        self.df['RSI'] = ta.momentum.rsi(self.df['Close'])
        
        # Stochastic Oscillator
        self.df['Stoch_k'] = ta.momentum.stoch(self.df['High'], self.df['Low'], self.df['Close'])
        self.df['Stoch_d'] = ta.momentum.stoch_signal(self.df['High'], self.df['Low'], self.df['Close'])
        
        # Williams %R
        self.df['Williams_R'] = ta.momentum.williams_r(self.df['High'], self.df['Low'], self.df['Close'])
        
        # ROC (Rate of Change)
        self.df['ROC'] = ta.momentum.roc(self.df['Close'])
        
    def _calculate_trend_indicators(self):
        """Calculate trend indicators"""
        # ADX
        self.df['ADX'] = ta.trend.adx(self.df['High'], self.df['Low'], self.df['Close'])
        self.df['DI_pos'] = ta.trend.adx_pos(self.df['High'], self.df['Low'], self.df['Close'])
        self.df['DI_neg'] = ta.trend.adx_neg(self.df['High'], self.df['Low'], self.df['Close'])
        
        # Parabolic SAR
        self.df['SAR'] = ta.trend.psar_up(self.df['High'], self.df['Low'], self.df['Close'])
        
        # CCI (Commodity Channel Index)
        self.df['CCI'] = ta.trend.cci(self.df['High'], self.df['Low'], self.df['Close'])
        
    def _calculate_volatility_indicators(self):
        """Calculate volatility indicators"""
        # Bollinger Bands
        self.df['BB_upper'] = ta.volatility.bollinger_hband(self.df['Close'])
        self.df['BB_middle'] = ta.volatility.bollinger_mavg(self.df['Close'])
        self.df['BB_lower'] = ta.volatility.bollinger_lband(self.df['Close'])
        
        # ATR
        self.df['ATR'] = ta.volatility.average_true_range(self.df['High'], self.df['Low'], self.df['Close'])
        
        # Keltner Channel
        self.df['KC_upper'] = ta.volatility.keltner_channel_hband(self.df['High'], self.df['Low'], self.df['Close'])
        self.df['KC_lower'] = ta.volatility.keltner_channel_lband(self.df['High'], self.df['Low'], self.df['Close'])
        
    def _calculate_volume_indicators(self):
        """Calculate volume-based indicators"""
        # On-Balance Volume (OBV)
        self.df['OBV'] = ta.volume.on_balance_volume(self.df['Close'], self.df['Volume'])
        
        # Volume Weighted Average Price (VWAP)
        self.df['VWAP'] = (self.df['Close'] * self.df['Volume']).cumsum() / self.df['Volume'].cumsum()
        
        # Money Flow Index (MFI)
        self.df['MFI'] = ta.volume.money_flow_index(self.df['High'], self.df['Low'], 
                                                   self.df['Close'], self.df['Volume'])
        
    def _calculate_support_resistance(self):
        """Calculate support and resistance levels"""
        # Using pivot points
        high = self.df['High'].iloc[-1]
        low = self.df['Low'].iloc[-1]
        close = self.df['Close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        
        self.indicators['support_resistance'] = {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            's1': s1,
            's2': s2
        }
        
    def generate_signals(self):
        """Generate trading signals based on technical indicators"""
        last_row = self.df.iloc[-1]
        
        # Moving Average Signals
        if last_row['SMA_50'] > last_row['SMA_200']:
            self.signals['bullish'].append("Golden Cross (SMA50 above SMA200)")
        elif last_row['SMA_50'] < last_row['SMA_200']:
            self.signals['bearish'].append("Death Cross (SMA50 below SMA200)")
            
        # RSI Signals
        if last_row['RSI'] > 70:
            self.signals['bearish'].append("RSI Overbought (>70)")
        elif last_row['RSI'] < 30:
            self.signals['bullish'].append("RSI Oversold (<30)")
            
        # MACD Signals
        if last_row['MACD_hist'] > 0 and self.df['MACD_hist'].iloc[-2] <= 0:
            self.signals['bullish'].append("MACD Bullish Crossover")
        elif last_row['MACD_hist'] < 0 and self.df['MACD_hist'].iloc[-2] >= 0:
            self.signals['bearish'].append("MACD Bearish Crossover")
            
        # Bollinger Bands Signals
        if last_row['Close'] < last_row['BB_lower']:
            self.signals['bullish'].append("Price below Lower Bollinger Band")
        elif last_row['Close'] > last_row['BB_upper']:
            self.signals['bearish'].append("Price above Upper Bollinger Band")
            
        # ADX Signals
        if last_row['ADX'] > 25:
            if last_row['DI_pos'] > last_row['DI_neg']:
                self.signals['bullish'].append("Strong Uptrend (ADX>25, +DI>-DI)")
            else:
                self.signals['bearish'].append("Strong Downtrend (ADX>25, +DI<-DI)")
                
        return self.signals
        
    def create_technical_chart(self):
        """Create technical analysis chart"""
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                           vertical_spacing=0.02,
                           row_heights=[0.4, 0.2, 0.2, 0.2])
        
        # Main candlestick chart
        fig.add_trace(go.Candlestick(x=self.df.index,
                                    open=self.df['Open'],
                                    high=self.df['High'],
                                    low=self.df['Low'],
                                    close=self.df['Close'],
                                    name='Price'),
                     row=1, col=1)
        
        # Add Bollinger Bands
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['BB_upper'],
                                name='BB Upper', line=dict(dash='dash')),
                     row=1, col=1)
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['BB_lower'],
                                name='BB Lower', line=dict(dash='dash')),
                     row=1, col=1)
        
        # Add Volume
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(self.df['Close'], self.df['Open'])]
        fig.add_trace(go.Bar(x=self.df.index, y=self.df['Volume'],
                            name='Volume', marker_color=colors),
                     row=2, col=1)
        
        # Add MACD
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['MACD_line'],
                                name='MACD'),
                     row=3, col=1)
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['MACD_signal'],
                                name='Signal'),
                     row=3, col=1)
        fig.add_trace(go.Bar(x=self.df.index, y=self.df['MACD_hist'],
                            name='MACD Histogram'),
                     row=3, col=1)
        
        # Add RSI
        fig.add_trace(go.Scatter(x=self.df.index, y=self.df['RSI'],
                                name='RSI'),
                     row=4, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=4, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=4, col=1)
        
        # Update layout
        fig.update_layout(
            title='Technical Analysis Chart',
            yaxis_title='Price',
            yaxis2_title='Volume',
            yaxis3_title='MACD',
            yaxis4_title='RSI',
            xaxis_rangeslider_visible=False,
            height=1000
        )
        
        return fig

def display_technical_analysis(df):
    """Display technical analysis dashboard"""
    # Initialize technical analysis
    ta_analyzer = TechnicalAnalysis(df)
    ta_analyzer.calculate_all_indicators()
    signals = ta_analyzer.generate_signals()
    
    # Display technical chart
    st.plotly_chart(ta_analyzer.create_technical_chart(), use_container_width=True)
    
    # Display signals
    st.header("Technical Signals")
    cols = st.columns(3)
    
    with cols[0]:
        st.subheader("Bullish Signals")
        for signal in signals['bullish']:
            st.success(signal)
            
    with cols[1]:
        st.subheader("Bearish Signals")
        for signal in signals['bearish']:
            st.warning(signal)
            
    with cols[2]:
        st.subheader("Neutral Signals")
        for signal in signals['neutral']:
            st.info(signal)
            
    # Display indicator values
    st.header("Current Indicator Values")
    indicator_cols = st.columns(4)
    
    # Last row of indicators
    last_row = ta_analyzer.df.iloc[-1]
    
    with indicator_cols[0]:
        st.metric("RSI", f"{last_row['RSI']:.2f}")
        st.metric("MACD", f"{last_row['MACD_line']:.2f}")
        
    with indicator_cols[1]:
        st.metric("ADX", f"{last_row['ADX']:.2f}")
        st.metric("CCI", f"{last_row['CCI']:.2f}")
        
    with indicator_cols[2]:
        st.metric("Stochastic %K", f"{last_row['Stoch_k']:.2f}")
        st.metric("Stochastic %D", f"{last_row['Stoch_d']:.2f}")
        
    with indicator_cols[3]:
        st.metric("Williams %R", f"{last_row['Williams_R']:.2f}")
        st.metric("ROC", f"{last_row['ROC']:.2f}")

if __name__ == "__main__":
    # Test with sample data
    symbol = "AAPL"
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1y")
    display_technical_analysis(df)