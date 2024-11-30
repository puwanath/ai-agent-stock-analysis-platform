"""
Company Information Display Component
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.thai_stock_fetcher import is_thai_stock

def format_currency(value, is_thai=False, decimal_places=2):
    """Format currency based on stock type"""
    if pd.isna(value) or value is None:
        return 'N/A'
    
    if is_thai:
        return f"฿{value:,.{decimal_places}f}"
    return f"${value:,.{decimal_places}f}"

def display_company_info(stock_info: dict):
    """Display enhanced company information"""
    
    # Determine if it's a Thai stock
    symbol = stock_info.get('symbol', '')
    is_thai = is_thai_stock(symbol)
    currency_symbol = '฿' if is_thai else '$'
    
    # Company Header
    st.header("Company Overview")
    
    # Current Price and Stock Statistics in Tabs
    st.subheader("Key Statistics")
    tabs = st.tabs([
        "Current Price", 
        "Market Data",
        "Trading Info",
        "Financials",
        "Additional Info"
    ])
    
    # Current Price Tab
    with tabs[0]:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = stock_info.get('currentPrice', 0)
            st.metric(
                "Current Price",
                format_currency(current_price, is_thai),
                delta=f"{stock_info.get('regularMarketChangePercent', 0):.2f}%",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Today's Range",
                f"{format_currency(stock_info.get('dayLow', 0), is_thai)} - "
                f"{format_currency(stock_info.get('dayHigh', 0), is_thai)}"
            )
            
        with col3:
            st.metric(
                "52 Week Range",
                f"{format_currency(stock_info.get('fiftyTwoWeekLow', 0), is_thai)} - "
                f"{format_currency(stock_info.get('fiftyTwoWeekHigh', 0), is_thai)}"
            )
            
        with col4:
            st.metric(
                "Volume",
                f"{stock_info.get('volume', 0):,}"
            )
            
        # Additional price metrics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Previous Close",
                format_currency(stock_info.get('previousClose', 0), is_thai)
            )
        
        with col2:
            st.metric(
                "Open",
                format_currency(stock_info.get('open', 0), is_thai)
            )
            
        with col3:
            st.metric(
                "Bid",
                format_currency(stock_info.get('bid', 0), is_thai)
            )
            
        with col4:
            st.metric(
                "Ask",
                format_currency(stock_info.get('ask', 0), is_thai)
            )
    
    # Market Data Tab
    with tabs[1]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Market Cap",
                format_market_cap(stock_info.get('marketCap', 0), is_thai)
            )
            st.metric(
                "Enterprise Value",
                format_market_cap(stock_info.get('enterpriseValue', 0), is_thai)
            )
            
        with col2:
            st.metric(
                "Beta",
                f"{stock_info.get('beta', 0):.2f}"
            )
            st.metric(
                "PE Ratio (TTM)",
                f"{stock_info.get('trailingPE', 0):.2f}"
            )
            
        with col3:
            st.metric(
                "EPS (TTM)",
                format_currency(stock_info.get('trailingEps', 0), is_thai)
            )
            st.metric(
                "Forward P/E",
                f"{stock_info.get('forwardPE', 0):.2f}"
            )
    
    # Trading Info Tab
    with tabs[2]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Avg. Volume (3m)",
                f"{stock_info.get('averageVolume3Month', 0):,}"
            )
            st.metric(
                "Avg. Volume (10d)",
                f"{stock_info.get('averageVolume10days', 0):,}"
            )
            
        with col2:
            st.metric(
                "Relative Volume",
                f"{stock_info.get('volume', 0) / stock_info.get('averageVolume', 1):.2f}x"
            )
            st.metric(
                "Previous Volume",
                f"{stock_info.get('previousVolume', 0):,}"
            )
            
        with col3:
            st.metric(
                "% Off High",
                f"{((stock_info.get('fiftyTwoWeekHigh', 0) - current_price) / stock_info.get('fiftyTwoWeekHigh', 1)) * 100:.2f}%"
            )
            st.metric(
                "% Off Low",
                f"{((current_price - stock_info.get('fiftyTwoWeekLow', 0)) / stock_info.get('fiftyTwoWeekLow', 1)) * 100:.2f}%"
            )
    
    # Financials Tab
    with tabs[3]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Revenue (TTM)",
                format_large_number(stock_info.get('totalRevenue', 0), is_thai)
            )
            st.metric(
                "Gross Profit",
                format_large_number(stock_info.get('grossProfits', 0), is_thai)
            )
            
        with col2:
            st.metric(
                "Profit Margin",
                f"{stock_info.get('profitMargins', 0)*100:.2f}%"
            )
            st.metric(
                "Operating Margin",
                f"{stock_info.get('operatingMargins', 0)*100:.2f}%"
            )
            
        with col3:
            st.metric(
                "Return on Equity",
                f"{stock_info.get('returnOnEquity', 0)*100:.2f}%"
            )
            st.metric(
                "Return on Assets",
                f"{stock_info.get('returnOnAssets', 0)*100:.2f}%"
            )
    
    # Additional Info Tab
    with tabs[4]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Dividend Yield",
                f"{stock_info.get('dividendYield', 0)*100:.2f}%" if stock_info.get('dividendYield') else "N/A"
            )
            st.metric(
                "Ex-Dividend Date",
                stock_info.get('exDividendDate', 'N/A')
            )
            
        with col2:
            st.metric(
                "Shares Outstanding",
                f"{stock_info.get('sharesOutstanding', 0):,}"
            )
            st.metric(
                "Float Shares",
                f"{stock_info.get('floatShares', 0):,}"
            )
            
        with col3:
            st.metric(
                "Short Ratio",
                f"{stock_info.get('shortRatio', 0):.2f}"
            )
            st.metric(
                "Short % of Float",
                f"{stock_info.get('shortPercentOfFloat', 0)*100:.2f}%" if stock_info.get('shortPercentOfFloat') else "N/A"
            )

def format_market_cap(value, is_thai=False):
    """Format market cap value"""
    if not value:
        return 'N/A'
    
    currency = '฿' if is_thai else '$'
    
    if value >= 1e12:
        return f'{currency}{value/1e12:.2f}T'
    elif value >= 1e9:
        return f'{currency}{value/1e9:.2f}B'
    elif value >= 1e6:
        return f'{currency}{value/1e6:.2f}M'
    else:
        return f'{currency}{value:,.0f}'

def format_large_number(value, is_thai=False):
    """Format large numbers"""
    if not value:
        return 'N/A'
    
    currency = '฿' if is_thai else '$'
    
    if value >= 1e9:
        return f'{currency}{value/1e9:.2f}B'
    elif value >= 1e6:
        return f'{currency}{value/1e6:.2f}M'
    elif value >= 1e3:
        return f'{currency}{value/1e3:.2f}K'
    return f'{currency}{value:,.0f}'