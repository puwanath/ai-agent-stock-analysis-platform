"""
Thai Stock Data Fetcher Module
Handles fetching data for Thai stocks from SET and other sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List, Any
import json
import time

class ThaiStockFetcher:
    def __init__(self):
        """Initialize Thai stock data fetcher"""
        self.set_url = "https://www.set.or.th"
        self.set_api_url = "https://www.set.or.th/api/set"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
    def _format_symbol(self, symbol: str) -> str:
        """Format symbol for Thai stocks"""
        symbol = symbol.upper().strip()
        if not symbol.endswith('.BK'):
            symbol = f"{symbol}.BK"
        return symbol

    async def fetch_stock_data(
        self,
        symbol: str,
        period: str = "1y"
    ) -> Tuple[Optional[pd.DataFrame], Dict]:
        """
        Fetch Thai stock data and information
        
        Args:
            symbol: Stock symbol (e.g., 'PTT', 'SCB', 'AOT')
            period: Time period for historical data
            
        Returns:
            Tuple of (DataFrame with OHLCV data, Dict with stock info)
        """
        formatted_symbol = self._format_symbol(symbol)
        base_symbol = symbol.replace('.BK', '')
        
        try:
            # Fetch historical data from Yahoo Finance
            stock = yf.Ticker(formatted_symbol)
            df = stock.history(period=period)
            
            # Fetch SET-specific information
            set_info = await self.fetch_set_info(base_symbol)
            financial_data = await self.fetch_financial_data(base_symbol)
            company_profile = await self.fetch_company_profile(base_symbol)
            
            # Combine all information
            info = {
                **stock.info,
                **set_info,
                'financial_data': financial_data,
                'company_profile': company_profile
            }
            
            return df, info
            
        except Exception as e:
            print(f"Error fetching Thai stock data: {e}")
            return None, {}

    async def fetch_set_info(self, symbol: str) -> Dict:
        """
        Fetch SET-specific stock information
        
        Args:
            symbol: Stock symbol without .BK
            
        Returns:
            Dictionary with SET-specific information
        """
        try:
            url = f"{self.set_api_url}/stock/{symbol}/info"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'marketCap': data.get('marketCap'),
                    'sector': data.get('sector'),
                    'industry': data.get('industry'),
                    'listedShare': data.get('listedShare'),
                    'par': data.get('par'),
                    'eps': data.get('eps')
                }
        except Exception as e:
            print(f"Error fetching SET info: {e}")
        return {}

    async def fetch_financial_data(self, symbol: str) -> Dict:
        """
        Fetch financial data from SET
        
        Args:
            symbol: Stock symbol without .BK
            
        Returns:
            Dictionary with financial data
        """
        try:
            url = f"{self.set_api_url}/stock/{symbol}/financials"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'balance_sheet': self._process_financial_statement(data.get('balanceSheet', [])),
                    'income_statement': self._process_financial_statement(data.get('incomeStatement', [])),
                    'cash_flow': self._process_financial_statement(data.get('cashFlow', [])),
                    'financial_ratios': self._process_financial_ratios(data.get('ratios', []))
                }
        except Exception as e:
            print(f"Error fetching financial data: {e}")
        return {}

    async def fetch_company_profile(self, symbol: str) -> Dict:
        """
        Fetch company profile from SET
        
        Args:
            symbol: Stock symbol without .BK
            
        Returns:
            Dictionary with company profile
        """
        try:
            url = f"{self.set_api_url}/stock/{symbol}/company"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'company_name_th': data.get('companyNameTH'),
                    'company_name_en': data.get('companyNameEN'),
                    'business_type': data.get('businessType'),
                    'website': data.get('website'),
                    'established_date': data.get('establishedDate'),
                    'market': data.get('market'),
                    'industry_group': data.get('industryGroup'),
                    'major_shareholders': self._process_shareholders(data.get('majorShareholders', []))
                }
        except Exception as e:
            print(f"Error fetching company profile: {e}")
        return {}

    async def fetch_realtime_quote(self, symbol: str) -> Dict:
        """
        Fetch realtime quote for Thai stock
        
        Args:
            symbol: Stock symbol without .BK
            
        Returns:
            Dictionary with realtime quote data
        """
        try:
            url = f"{self.set_api_url}/stock/{symbol}/realtime"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'last_price': data.get('last'),
                    'change': data.get('change'),
                    'change_percent': data.get('percentChange'),
                    'bid': data.get('bid'),
                    'offer': data.get('offer'),
                    'volume': data.get('volume'),
                    'value': data.get('value'),
                    'high': data.get('high'),
                    'low': data.get('low'),
                    'timestamp': data.get('timestamp')
                }
        except Exception as e:
            print(f"Error fetching realtime quote: {e}")
        return {}

    def _process_financial_statement(self, data: List) -> pd.DataFrame:
        """Process financial statement data into DataFrame"""
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def _process_financial_ratios(self, data: List) -> pd.DataFrame:
        """Process financial ratios into DataFrame"""
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def _process_shareholders(self, data: List) -> pd.DataFrame:
        """Process shareholders data into DataFrame"""
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)

    async def fetch_market_data(self) -> Dict:
        """
        Fetch SET market data
        
        Returns:
            Dictionary with market data
        """
        try:
            url = f"{self.set_api_url}/market/summary"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'set_index': data.get('setIndex'),
                    'set_change': data.get('setChange'),
                    'set_volume': data.get('setVolume'),
                    'set_value': data.get('setValue'),
                    'market_status': data.get('marketStatus'),
                    'last_update': data.get('lastUpdate')
                }
        except Exception as e:
            print(f"Error fetching market data: {e}")
        return {}

    async def fetch_sector_performance(self) -> pd.DataFrame:
        """
        Fetch SET sector performance
        
        Returns:
            DataFrame with sector performance data
        """
        try:
            url = f"{self.set_api_url}/market/sectors"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching sector performance: {e}")
        return pd.DataFrame()

    async def fetch_top_movers(self, category: str = 'value') -> pd.DataFrame:
        """
        Fetch top movers from SET
        
        Args:
            category: 'value', 'gainers', 'losers', or 'volume'
            
        Returns:
            DataFrame with top movers
        """
        try:
            url = f"{self.set_api_url}/market/ranking/{category}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching top movers: {e}")
        return pd.DataFrame()

def is_thai_stock(symbol: str) -> bool:
    """Check if symbol is a Thai stock"""
    return symbol.upper().endswith('.BK') or len(symbol) <= 4

def format_thai_number(value: float) -> str:
    """Format number for Thai display"""
    if pd.isna(value) or value is None:
        return 'N/A'
    
    if abs(value) >= 1e9:
        return f'{value/1e9:.2f}B'
    elif abs(value) >= 1e6:
        return f'{value/1e6:.2f}M'
    elif abs(value) >= 1e3:
        return f'{value/1e3:.2f}K'
    
    return f'{value:,.2f}'