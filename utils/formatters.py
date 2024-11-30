"""
Formatters Module
Contains utilities for formatting various types of financial and numerical data.
"""

from typing import Union, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import locale
from decimal import Decimal

# Set locale for currency formatting
locale.setlocale(locale.LC_ALL, '')

class NumberFormatter:
    """Class for number formatting utilities"""
    
    @staticmethod
    def format_currency(
        value: Union[float, int],
        precision: int = 2,
        currency_symbol: str = '$',
        show_zeros: bool = False
    ) -> str:
        """
        Format number as currency
        
        Args:
            value: Number to format
            precision: Decimal precision
            currency_symbol: Currency symbol to use
            show_zeros: Whether to show zero values or return empty string
            
        Returns:
            Formatted currency string
        """
        if pd.isna(value) or value is None:
            return 'N/A'
            
        if value == 0 and not show_zeros:
            return ''
            
        try:
            return f"{currency_symbol}{value:,.{precision}f}"
        except:
            return 'N/A'

    @staticmethod
    def format_large_number(
        value: Union[float, int],
        precision: int = 1,
        include_symbol: bool = True
    ) -> str:
        """
        Format large numbers with K, M, B, T suffixes
        
        Args:
            value: Number to format
            precision: Decimal precision
            include_symbol: Whether to include suffix symbol
            
        Returns:
            Formatted string
        """
        if pd.isna(value) or value is None:
            return 'N/A'
            
        try:
            abs_value = abs(float(value))
            if abs_value >= 1e12:
                formatted = f"{value/1e12:.{precision}f}"
                suffix = 'T' if include_symbol else ''
            elif abs_value >= 1e9:
                formatted = f"{value/1e9:.{precision}f}"
                suffix = 'B' if include_symbol else ''
            elif abs_value >= 1e6:
                formatted = f"{value/1e6:.{precision}f}"
                suffix = 'M' if include_symbol else ''
            elif abs_value >= 1e3:
                formatted = f"{value/1e3:.{precision}f}"
                suffix = 'K' if include_symbol else ''
            else:
                formatted = f"{value:.{precision}f}"
                suffix = ''
            return f"{formatted}{suffix}"
        except:
            return 'N/A'

    @staticmethod
    def format_percentage(
        value: Union[float, int],
        precision: int = 2,
        include_symbol: bool = True,
        multiply: bool = True
    ) -> str:
        """
        Format number as percentage
        
        Args:
            value: Number to format
            precision: Decimal precision
            include_symbol: Whether to include % symbol
            multiply: Whether to multiply by 100
            
        Returns:
            Formatted percentage string
        """
        if pd.isna(value) or value is None:
            return 'N/A'
            
        try:
            if multiply:
                value *= 100
            formatted = f"{value:.{precision}f}"
            symbol = '%' if include_symbol else ''
            return f"{formatted}{symbol}"
        except:
            return 'N/A'

class DateFormatter:
    """Class for date formatting utilities"""
    
    @staticmethod
    def format_date(
        date: Union[str, datetime],
        format_str: str = '%Y-%m-%d'
    ) -> str:
        """
        Format date to string
        
        Args:
            date: Date to format
            format_str: Date format string
            
        Returns:
            Formatted date string
        """
        if pd.isna(date):
            return 'N/A'
            
        try:
            if isinstance(date, str):
                date = pd.to_datetime(date)
            return date.strftime(format_str)
        except:
            return 'N/A'

    @staticmethod
    def format_time_ago(date: datetime) -> str:
        """
        Format date as time ago (e.g., "2 hours ago")
        
        Args:
            date: Date to format
            
        Returns:
            Formatted time ago string
        """
        if pd.isna(date):
            return 'N/A'
            
        try:
            now = datetime.now()
            diff = now - date
            
            if diff.days > 365:
                years = diff.days // 365
                return f"{years}y ago"
            elif diff.days > 30:
                months = diff.days // 30
                return f"{months}mo ago"
            elif diff.days > 0:
                return f"{diff.days}d ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours}h ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes}m ago"
            else:
                return f"{diff.seconds}s ago"
        except:
            return 'N/A'

class MetricFormatter:
    """Class for formatting financial metrics"""
    
    @staticmethod
    def format_change(
        current: float,
        previous: float,
        as_percentage: bool = True,
        precision: int = 2,
        include_symbol: bool = True
    ) -> str:
        """
        Format change between two values
        
        Args:
            current: Current value
            previous: Previous value
            as_percentage: Return as percentage if True
            precision: Decimal precision
            include_symbol: Whether to include symbols
            
        Returns:
            Formatted change string
        """
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return 'N/A'
            
        try:
            change = (current - previous) / abs(previous)
            if as_percentage:
                change *= 100
                symbol = '%' if include_symbol else ''
            else:
                symbol = 'x' if include_symbol else ''
                
            sign = '+' if change > 0 and include_symbol else ''
            return f"{sign}{change:.{precision}f}{symbol}"
        except:
            return 'N/A'

    @staticmethod
    def format_ratio(
        numerator: float,
        denominator: float,
        precision: int = 2
    ) -> str:
        """
        Format financial ratio
        
        Args:
            numerator: Numerator value
            denominator: Denominator value
            precision: Decimal precision
            
        Returns:
            Formatted ratio string
        """
        if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
            return 'N/A'
            
        try:
            ratio = numerator / denominator
            return f"{ratio:.{precision}f}"
        except:
            return 'N/A'

def format_table_value(
    value: Any,
    format_type: str = 'number',
    precision: int = 2,
    prefix: str = '',
    suffix: str = ''
) -> str:
    """
    Format value for table display
    
    Args:
        value: Value to format
        format_type: Type of formatting to apply
        precision: Decimal precision
        prefix: Prefix to add
        suffix: Suffix to add
        
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return 'N/A'
        
    try:
        if format_type == 'currency':
            formatted = NumberFormatter.format_currency(value, precision)
        elif format_type == 'percentage':
            formatted = NumberFormatter.format_percentage(value, precision)
        elif format_type == 'large_number':
            formatted = NumberFormatter.format_large_number(value, precision)
        else:
            formatted = f"{value:.{precision}f}"
            
        return f"{prefix}{formatted}{suffix}"
    except:
        return 'N/A'

def format_df_values(
    df: pd.DataFrame,
    format_dict: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """
    Format DataFrame values according to format dictionary
    
    Args:
        df: DataFrame to format
        format_dict: Dictionary of column names and format parameters
        
    Returns:
        Formatted DataFrame
    """
    formatted_df = df.copy()
    
    for column, format_params in format_dict.items():
        if column in formatted_df.columns:
            formatted_df[column] = formatted_df[column].apply(
                lambda x: format_table_value(x, **format_params)
            )
            
    return formatted_df

def get_color_for_value(
    value: float,
    neutral_threshold: float = 0,
    is_percentage: bool = False
) -> str:
    """
    Get color for value based on whether it's positive/negative
    
    Args:
        value: Value to get color for
        neutral_threshold: Threshold for neutral color
        is_percentage: Whether value is a percentage
        
    Returns:
        Color string (hex code)
    """
    if pd.isna(value):
        return '#808080'  # Gray for N/A
        
    try:
        if is_percentage:
            value = value / 100
            
        if abs(value - neutral_threshold) < 1e-6:
            return '#808080'  # Gray for neutral
        elif value > neutral_threshold:
            return '#00CC00'  # Green for positive
        else:
            return '#FF0000'  # Red for negative
    except:
        return '#808080'  # Gray for errors