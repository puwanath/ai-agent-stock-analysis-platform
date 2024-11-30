"""
Utilities Module for Stock Analysis Platform
Contains common utilities and helper functions used across the application.
"""

from typing import Dict, List, Union, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Version Information
__version__ = '1.0.0'
__author__ = 'AI-Agents Finance Team'

# Type Aliases
Number = Union[int, float]
DateLike = Union[str, datetime]
DataFrameLike = Union[pd.DataFrame, pd.Series]

def format_number(value: Number, precision: int = 2, prefix: str = '') -> str:
    """
    Format number with proper scaling (K, M, B, T)
    
    Args:
        value: Number to format
        precision: Decimal precision
        prefix: Prefix to add (e.g., '$')
        
    Returns:
        Formatted string
    """
    if pd.isna(value) or value is None:
        return 'N/A'
        
    if abs(value) >= 1e12:
        return f'{prefix}{value/1e12:.{precision}f}T'
    elif abs(value) >= 1e9:
        return f'{prefix}{value/1e9:.{precision}f}B'
    elif abs(value) >= 1e6:
        return f'{prefix}{value/1e6:.{precision}f}M'
    elif abs(value) >= 1e3:
        return f'{prefix}{value/1e3:.{precision}f}K'
    else:
        return f'{prefix}{value:.{precision}f}'

def format_percentage(value: Number, precision: int = 2) -> str:
    """
    Format number as percentage
    
    Args:
        value: Number to format
        precision: Decimal precision
        
    Returns:
        Formatted percentage string
    """
    if pd.isna(value) or value is None:
        return 'N/A'
    return f'{value*100:.{precision}f}%'

def format_date(date: DateLike, fmt: str = '%Y-%m-%d') -> str:
    """
    Format date to string
    
    Args:
        date: Date to format
        fmt: Date format string
        
    Returns:
        Formatted date string
    """
    if isinstance(date, str):
        date = pd.to_datetime(date)
    return date.strftime(fmt)

def calculate_change(
    current: Number,
    previous: Number,
    percentage: bool = True
) -> float:
    """
    Calculate change between two values
    
    Args:
        current: Current value
        previous: Previous value
        percentage: Return as percentage if True
        
    Returns:
        Change value or percentage
    """
    if not previous:
        return 0
    change = (current - previous) / abs(previous)
    return change * 100 if percentage else change

def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str]
) -> bool:
    """
    Validate DataFrame has required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if valid, False otherwise
    """
    return all(col in df.columns for col in required_columns)

def rolling_window(
    df: pd.DataFrame,
    window: int,
    min_periods: Optional[int] = None
) -> pd.DataFrame:
    """
    Apply rolling window calculations safely
    
    Args:
        df: Input DataFrame
        window: Rolling window size
        min_periods: Minimum number of observations
        
    Returns:
        DataFrame with rolling calculations
    """
    if min_periods is None:
        min_periods = window
    return df.rolling(window=window, min_periods=min_periods)

def safe_request(
    url: str,
    max_retries: int = 3,
    delay: int = 1
) -> Optional[Any]:
    """
    Make HTTP request with retry logic
    
    Args:
        url: URL to request
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds
        
    Returns:
        Response data or None if failed
    """
    import requests
    import time
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Request failed after {max_retries} attempts: {e}")
                return None
            time.sleep(delay)

class DataValidationError(Exception):
    """Exception raised for data validation errors"""
    pass

class DateRangeError(Exception):
    """Exception raised for invalid date ranges"""
    pass

class CalculationError(Exception):
    """Exception raised for calculation errors"""
    pass

def validate_date_range(
    start_date: DateLike,
    end_date: DateLike,
    min_days: int = 0,
    max_days: Optional[int] = None
) -> bool:
    """
    Validate a date range
    
    Args:
        start_date: Start date
        end_date: End date
        min_days: Minimum number of days required
        max_days: Maximum number of days allowed
        
    Returns:
        True if valid, raises DateRangeError otherwise
    """
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    days = (end - start).days
    
    if days < min_days:
        raise DateRangeError(f"Date range must be at least {min_days} days")
    
    if max_days and days > max_days:
        raise DateRangeError(f"Date range cannot exceed {max_days} days")
    
    return True

def moving_average(
    data: Union[List[Number], np.ndarray, pd.Series],
    window: int,
    type: str = 'simple'
) -> np.ndarray:
    """
    Calculate moving average
    
    Args:
        data: Input data
        window: Window size
        type: 'simple' or 'exponential'
        
    Returns:
        Array of moving averages
    """
    if isinstance(data, (list, pd.Series)):
        data = np.array(data)
    
    if type == 'simple':
        weights = np.ones(window)
    elif type == 'exponential':
        weights = np.exp(np.linspace(-1., 0., window))
    else:
        raise ValueError(f"Unknown moving average type: {type}")
    
    weights /= weights.sum()
    return np.convolve(data, weights, mode='valid')

# Export all utilities
__all__ = [
    'format_number',
    'format_percentage',
    'format_date',
    'calculate_change',
    'validate_dataframe',
    'rolling_window',
    'safe_request',
    'validate_date_range',
    'moving_average',
    'DataValidationError',
    'DateRangeError',
    'CalculationError'
]