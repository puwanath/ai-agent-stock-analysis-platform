"""
Financial Metrics Utility Module
Handles calculation and formatting of financial metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from utils.thai_stock_fetcher import is_thai_stock

class FinancialMetricsCalculator:
    def __init__(self, stock_info: Dict):
        """
        Initialize calculator with stock information
        
        Args:
            stock_info: Dictionary containing stock information
        """
        self.stock_info = stock_info
        self.symbol = stock_info.get('symbol', '')
        self.is_thai = is_thai_stock(self.symbol)
        self.currency = '฿' if self.is_thai else '$'

    def format_currency(self, value: float, precision: int = 2) -> str:
        """Format currency with appropriate symbol"""
        if pd.isna(value) or value is None:
            return 'N/A'
        return f"{self.currency}{value:,.{precision}f}"

    def format_large_number(self, value: float) -> str:
        """Format large numbers with currency and scale"""
        if pd.isna(value) or value is None:
            return 'N/A'
        
        if value >= 1e12:
            return f"{self.currency}{value/1e12:.2f}T"
        elif value >= 1e9:
            return f"{self.currency}{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{self.currency}{value/1e6:.2f}M"
        return self.format_currency(value)

    def format_percentage(self, value: float) -> str:
        """Format value as percentage"""
        if pd.isna(value) or value is None:
            return 'N/A'
        return f"{value*100:.2f}%"

    def get_valuation_metrics(self) -> Dict:
        """Get valuation metrics"""
        return {
            'Market Cap': self.format_large_number(self.stock_info.get('marketCap')),
            'Enterprise Value': self.format_large_number(self.stock_info.get('enterpriseValue')),
            'P/E Ratio': f"{self.stock_info.get('trailingPE', 0):.2f}",
            'Forward P/E': f"{self.stock_info.get('forwardPE', 0):.2f}",
            'PEG Ratio': f"{self.stock_info.get('pegRatio', 0):.2f}",
            'Price/Book': f"{self.stock_info.get('priceToBook', 0):.2f}",
            'Price/Sales': f"{self.stock_info.get('priceToSalesTrailing12Months', 0):.2f}",
            'EV/EBITDA': f"{self.stock_info.get('enterpriseToEbitda', 0):.2f}"
        }

    def get_profitability_metrics(self) -> Dict:
        """Get profitability metrics"""
        return {
            'Gross Margin': self.format_percentage(self.stock_info.get('grossMargins')),
            'Operating Margin': self.format_percentage(self.stock_info.get('operatingMargins')),
            'Profit Margin': self.format_percentage(self.stock_info.get('profitMargins')),
            'ROE': self.format_percentage(self.stock_info.get('returnOnEquity')),
            'ROA': self.format_percentage(self.stock_info.get('returnOnAssets')),
            'ROIC': self.format_percentage(self.stock_info.get('returnOnCapital'))
        }

    def get_growth_metrics(self) -> Dict:
        """Get growth metrics"""
        return {
            'Revenue Growth': self.format_percentage(self.stock_info.get('revenueGrowth')),
            'Earnings Growth': self.format_percentage(self.stock_info.get('earningsGrowth')),
            'EPS Growth': self.format_percentage(self.stock_info.get('earningsQuarterlyGrowth')),
            '5Y Revenue CAGR': self.format_percentage(self.stock_info.get('revenuePerShare5Y')),
            '5Y Earnings CAGR': self.format_percentage(self.stock_info.get('earningsPerShare5Y'))
        }

    def get_financial_strength(self) -> Dict:
        """Get financial strength metrics"""
        return {
            'Current Ratio': f"{self.stock_info.get('currentRatio', 0):.2f}",
            'Quick Ratio': f"{self.stock_info.get('quickRatio', 0):.2f}",
            'Debt/Equity': f"{self.stock_info.get('debtToEquity', 0):.2f}",
            'Interest Coverage': f"{self.stock_info.get('interestCoverage', 0):.2f}",
            'Total Cash': self.format_large_number(self.stock_info.get('totalCash')),
            'Total Debt': self.format_large_number(self.stock_info.get('totalDebt'))
        }

    def get_efficiency_metrics(self) -> Dict:
        """Get efficiency metrics"""
        return {
            'Asset Turnover': f"{self.stock_info.get('assetTurnover', 0):.2f}",
            'Inventory Turnover': f"{self.stock_info.get('inventoryTurnover', 0):.2f}",
            'Days Sales Outstanding': f"{self.stock_info.get('daysSalesOutstanding', 0):.1f}",
            'Days Inventory': f"{self.stock_info.get('daysInventory', 0):.1f}",
            'Operating Cycle': f"{self.stock_info.get('operatingCycle', 0):.1f}"
        }

    def get_dividend_metrics(self) -> Dict:
        """Get dividend metrics"""
        return {
            'Dividend Rate': self.format_currency(self.stock_info.get('dividendRate')),
            'Dividend Yield': self.format_percentage(self.stock_info.get('dividendYield')),
            'Payout Ratio': self.format_percentage(self.stock_info.get('payoutRatio')),
            '5Y Avg Dividend Yield': self.format_percentage(self.stock_info.get('fiveYearAvgDividendYield')),
            'Dividend Growth': self.format_percentage(self.stock_info.get('dividendGrowth'))
        }

def get_financial_metrics(stock_info: Dict) -> Dict:
    """
    Get comprehensive financial metrics
    
    Args:
        stock_info: Dictionary containing stock information
        
    Returns:
        Dictionary with all financial metrics
    """
    calculator = FinancialMetricsCalculator(stock_info)
    
    try:
        metrics = {
            'Valuation': calculator.get_valuation_metrics(),
            'Profitability': calculator.get_profitability_metrics(),
            'Growth': calculator.get_growth_metrics(),
            'Financial_Strength': calculator.get_financial_strength(),
            'Efficiency': calculator.get_efficiency_metrics(),
            'Dividend': calculator.get_dividend_metrics()
        }
        
        # Add fundamental scores
        metrics['Scores'] = calculate_fundamental_scores(metrics)
        
        return metrics
        
    except Exception as e:
        print(f"Error calculating financial metrics: {e}")
        return {}

def calculate_fundamental_scores(metrics: Dict) -> Dict:
    """
    Calculate fundamental analysis scores
    
    Args:
        metrics: Dictionary of financial metrics
        
    Returns:
        Dictionary with scores for different aspects
    """
    scores = {}
    
    try:
        # Valuation Score (0-100, lower is better)
        pe_ratio = float(metrics['Valuation']['P/E Ratio'].replace('N/A', '0'))
        pb_ratio = float(metrics['Valuation']['Price/Book'].replace('N/A', '0'))
        
        if pe_ratio > 0:
            valuation_score = min(100, max(0, (pe_ratio/30 + pb_ratio/3) * 50))
        else:
            valuation_score = 50  # Neutral if PE is negative
            
        scores['Valuation_Score'] = valuation_score
        
        # Profitability Score (0-100, higher is better)
        profit_margin = float(metrics['Profitability']['Profit Margin'].replace('%', '').replace('N/A', '0'))
        roe = float(metrics['Profitability']['ROE'].replace('%', '').replace('N/A', '0'))
        
        profitability_score = min(100, max(0, profit_margin * 3 + roe * 2))
        scores['Profitability_Score'] = profitability_score
        
        # Growth Score (0-100, higher is better)
        revenue_growth = float(metrics['Growth']['Revenue Growth'].replace('%', '').replace('N/A', '0'))
        earnings_growth = float(metrics['Growth']['Earnings Growth'].replace('%', '').replace('N/A', '0'))
        
        growth_score = min(100, max(0, (revenue_growth + earnings_growth) * 2.5))
        scores['Growth_Score'] = growth_score
        
        # Financial Health Score (0-100, higher is better)
        current_ratio = float(metrics['Financial_Strength']['Current Ratio'].replace('N/A', '0'))
        debt_equity = float(metrics['Financial_Strength']['Debt/Equity'].replace('N/A', '0'))
        
        health_score = min(100, max(0, current_ratio * 30 - debt_equity * 10 + 50))
        scores['Financial_Health_Score'] = health_score
        
        # Overall Score
        scores['Overall_Score'] = (
            valuation_score * 0.3 +
            profitability_score * 0.25 +
            growth_score * 0.25 +
            health_score * 0.2
        )
        
        return scores
        
    except Exception as e:
        print(f"Error calculating fundamental scores: {e}")
        return {
            'Valuation_Score': 50,
            'Profitability_Score': 50,
            'Growth_Score': 50,
            'Financial_Health_Score': 50,
            'Overall_Score': 50
        }

def interpret_financial_metrics(metrics: Dict) -> str:
    """
    Generate human-readable interpretation of financial metrics
    
    Args:
        metrics: Dictionary of financial metrics
        
    Returns:
        String with interpretation
    """
    interpretation = []
    
    try:
        # Valuation interpretation
        pe_ratio = float(metrics['Valuation']['P/E Ratio'].replace('N/A', '0'))
        if pe_ratio > 30:
            interpretation.append("🔴 Stock appears expensive based on P/E ratio")
        elif pe_ratio > 15:
            interpretation.append("🟡 Stock is moderately valued based on P/E ratio")
        elif pe_ratio > 0:
            interpretation.append("🟢 Stock appears attractively valued based on P/E ratio")
        
        # Profitability interpretation
        profit_margin = float(metrics['Profitability']['Profit Margin'].replace('%', '').replace('N/A', '0'))
        if profit_margin > 20:
            interpretation.append("🟢 Company shows strong profitability")
        elif profit_margin > 10:
            interpretation.append("🟡 Company shows moderate profitability")
        else:
            interpretation.append("🔴 Company shows weak profitability")
        
        # Growth interpretation
        revenue_growth = float(metrics['Growth']['Revenue Growth'].replace('%', '').replace('N/A', '0'))
        if revenue_growth > 20:
            interpretation.append("🟢 Strong revenue growth")
        elif revenue_growth > 10:
            interpretation.append("🟡 Moderate revenue growth")
        else:
            interpretation.append("🔴 Weak revenue growth")
        
        # Financial health interpretation
        current_ratio = float(metrics['Financial_Strength']['Current Ratio'].replace('N/A', '0'))
        if current_ratio > 2:
            interpretation.append("🟢 Strong financial health")
        elif current_ratio > 1:
            interpretation.append("🟡 Adequate financial health")
        else:
            interpretation.append("🔴 Weak financial health")
        
        # Overall score interpretation
        overall_score = metrics['Scores']['Overall_Score']
        if overall_score > 70:
            interpretation.append("🟢 Overall: Strong fundamental metrics")
        elif overall_score > 50:
            interpretation.append("🟡 Overall: Average fundamental metrics")
        else:
            interpretation.append("🔴 Overall: Weak fundamental metrics")
        
        return "\n".join(interpretation)
        
    except Exception as e:
        print(f"Error interpreting financial metrics: {e}")
        return "Unable to interpret financial metrics"