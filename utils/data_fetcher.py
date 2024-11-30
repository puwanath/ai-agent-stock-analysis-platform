"""
Data Fetcher Module
Handles all data retrieval operations for the stock analysis platform.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional, Tuple, Union
import asyncio
import aiohttp
import time

class DataFetcher:
    """Main class for fetching financial data"""
    
    def __init__(self, cache_enabled: bool = True, cache_timeout: int = 3600):
        """
        Initialize DataFetcher
        
        Args:
            cache_enabled: Whether to enable caching
            cache_timeout: Cache timeout in seconds
        """
        self.cache_enabled = cache_enabled
        self.cache_timeout = cache_timeout
        self.cache = {}
        self.last_request = 0
        self.request_delay = 0.1  # 100ms delay between requests
        
    async def fetch_stock_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> Tuple[Optional[pd.DataFrame], Optional[Dict]]:
        """
        Fetch stock data and info from Yahoo Finance
        
        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            Tuple of (DataFrame with OHLCV data, Dict with stock info)
        """
        try:
            cache_key = f"{symbol}_{period}_{interval}"
            if self.cache_enabled and cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if time.time() - cached_time < self.cache_timeout:
                    return cached_data

            # Add delay between requests
            current_time = time.time()
            if current_time - self.last_request < self.request_delay:
                await asyncio.sleep(self.request_delay)
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            info = ticker.info
            
            if self.cache_enabled:
                self.cache[cache_key] = ((df, info), time.time())
            
            self.last_request = time.time()
            return df, info
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None, None

    async def fetch_multiple_stocks(
        self,
        symbols: List[str],
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, Tuple[Optional[pd.DataFrame], Optional[Dict]]]:
        """
        Fetch data for multiple stocks concurrently
        
        Args:
            symbols: List of stock symbols
            period: Time period
            interval: Data interval
            
        Returns:
            Dictionary of symbol -> (DataFrame, info_dict)
        """
        async def fetch_single(symbol):
            return symbol, await self.fetch_stock_data(symbol, period, interval)
        
        tasks = [fetch_single(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        return dict(results)

    async def fetch_market_data(
        self,
        index_symbol: str = "^GSPC",
        sector_etfs: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch market-wide data including index and sector performance
        
        Args:
            index_symbol: Market index symbol
            sector_etfs: List of sector ETF symbols
            
        Returns:
            Dictionary of DataFrames with market data
        """
        if sector_etfs is None:
            sector_etfs = [
                "XLK",  # Technology
                "XLF",  # Financials
                "XLV",  # Healthcare
                "XLE",  # Energy
                "XLI",  # Industrials
                "XLC",  # Communication Services
                "XLY",  # Consumer Discretionary
                "XLP",  # Consumer Staples
                "XLB",  # Materials
                "XLRE" # Real Estate
            ]
        
        symbols = [index_symbol] + sector_etfs
        data = await self.fetch_multiple_stocks(symbols)
        return {symbol: df for symbol, (df, _) in data.items() if df is not None}

    async def fetch_fundamental_data(
        self,
        symbol: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch fundamental financial data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary of financial statements
        """
        try:
            ticker = yf.Ticker(symbol)
            return {
                'income_statement': ticker.financials,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow,
                'earnings': ticker.earnings,
                'recommendations': ticker.recommendations
            }
        except Exception as e:
            print(f"Error fetching fundamental data for {symbol}: {str(e)}")
            return {}

    async def fetch_economic_indicators(
        self,
        indicators: Optional[List[str]] = None
    ) -> Dict[str, pd.Series]:
        """
        Fetch economic indicators from FRED
        
        Args:
            indicators: List of FRED indicator codes
            
        Returns:
            Dictionary of indicator data
        """
        if indicators is None:
            indicators = [
                "GDP",           # Gross Domestic Product
                "UNRATE",        # Unemployment Rate
                "CPIAUCSL",      # Consumer Price Index
                "DFF",           # Federal Funds Rate
                "T10Y2Y"         # 10-Year Treasury Constant Maturity Minus 2-Year
            ]
        
        # Implementation would require FRED API key
        # Placeholder for demonstration
        return {}

    def get_market_hours(
        self,
        exchange: str = "NYSE"
    ) -> Dict[str, datetime]:
        """
        Get market trading hours
        
        Args:
            exchange: Exchange name
            
        Returns:
            Dictionary with market hours
        """
        # Placeholder implementation
        eastern_tz = datetime.now()
        market_open = eastern_tz.replace(hour=9, minute=30, second=0)
        market_close = eastern_tz.replace(hour=16, minute=0, second=0)
        
        return {
            "market_open": market_open,
            "market_close": market_close,
            "is_open": market_open <= eastern_tz <= market_close
        }

    def clear_cache(self):
        """Clear the data cache"""
        self.cache = {}

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info
        except:
            return False

class MarketDataFetcher:
    """Class for fetching real-time market data"""
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
        
    async def close(self):
        """Close the aiohttp session"""
        await self.session.close()
        
    async def get_quote(
        self,
        symbol: str
    ) -> Optional[Dict]:
        """
        Get real-time quote for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with quote data
        """
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {str(e)}")
            return None
            
    async def get_market_movers(
        self,
        n_stocks: int = 10
    ) -> Dict[str, List[Dict]]:
        """
        Get top market movers
        
        Args:
            n_stocks: Number of stocks to fetch
            
        Returns:
            Dictionary with gainers, losers, and most active stocks
        """
        try:
            # This would typically use a market data API
            # Placeholder implementation
            return {
                "gainers": [],
                "losers": [],
                "most_active": []
            }
        except Exception as e:
            print(f"Error fetching market movers: {str(e)}")
            return {}

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

def validate_ohlcv_data(df: pd.DataFrame) -> bool:
    """
    Validate OHLCV data
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid, raises DataValidationError otherwise
    """
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    if not all(col in df.columns for col in required_columns):
        raise DataValidationError("Missing required columns in OHLCV data")
        
    if df.empty:
        raise DataValidationError("Empty dataset")
        
    if df.isnull().any().any():
        raise DataValidationError("Dataset contains missing values")
        
    return True

async def get_data_fetcher() -> DataFetcher:
    """
    Factory function to get DataFetcher instance
    
    Returns:
        Configured DataFetcher instance
    """
    return DataFetcher(cache_enabled=True)