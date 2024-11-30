"""
Financial Analysis Component
Handles financial metrics and ratio display with appropriate currency formatting
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.thai_stock_fetcher import is_thai_stock

class FinancialAnalyzer:
    def __init__(self, stock_info: dict):
        """Initialize with stock information"""
        self.stock_info = stock_info
        self.symbol = stock_info.get('symbol', '')
        self.is_thai = is_thai_stock(self.symbol)
        self.currency_symbol = '฿' if self.is_thai else '$'

    def format_currency(self, value: float, precision: int = 2) -> str:
        """Format currency with appropriate symbol"""
        if pd.isna(value) or value is None:
            return 'N/A'
        return f"{self.currency_symbol}{value:,.{precision}f}"

    def format_large_number(self, value: float) -> str:
        """Format large numbers with currency"""
        if pd.isna(value) or value is None:
            return 'N/A'
            
        if value >= 1e12:
            return f"{self.currency_symbol}{value/1e12:.2f}T"
        elif value >= 1e9:
            return f"{self.currency_symbol}{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{self.currency_symbol}{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{self.currency_symbol}{value/1e3:.2f}K"
        return self.format_currency(value)

    def format_percentage(self, value: float) -> str:
        """Format value as percentage"""
        if pd.isna(value) or value is None:
            return 'N/A'
        return f"{value*100:.2f}%"

    def get_income_statement_metrics(self) -> dict:
        """Get key income statement metrics"""
        return {
            "Revenue": self.format_large_number(self.stock_info.get('totalRevenue')),
            "Revenue Growth": self.format_percentage(self.stock_info.get('revenueGrowth')),
            "Gross Profit": self.format_large_number(self.stock_info.get('grossProfits')),
            "EBITDA": self.format_large_number(self.stock_info.get('ebitda')),
            "Net Income": self.format_large_number(self.stock_info.get('netIncomeToCommon')),
            "EPS": self.format_currency(self.stock_info.get('trailingEps')),
            "Forward EPS": self.format_currency(self.stock_info.get('forwardEps')),
        }

    def get_balance_sheet_metrics(self) -> dict:
        """Get key balance sheet metrics"""
        return {
            "Total Assets": self.format_large_number(self.stock_info.get('totalAssets')),
            "Total Debt": self.format_large_number(self.stock_info.get('totalDebt')),
            "Total Cash": self.format_large_number(self.stock_info.get('totalCash')),
            "Book Value": self.format_currency(self.stock_info.get('bookValue')),
            "Cash Per Share": self.format_currency(self.stock_info.get('totalCashPerShare')),
        }

    def get_valuation_metrics(self) -> dict:
        """Get key valuation metrics"""
        return {
            "Market Cap": self.format_large_number(self.stock_info.get('marketCap')),
            "Enterprise Value": self.format_large_number(self.stock_info.get('enterpriseValue')),
            "P/E Ratio": f"{self.stock_info.get('trailingPE', 0):.2f}",
            "Forward P/E": f"{self.stock_info.get('forwardPE', 0):.2f}",
            "PEG Ratio": f"{self.stock_info.get('pegRatio', 0):.2f}",
            "Price/Book": f"{self.stock_info.get('priceToBook', 0):.2f}",
            "Price/Sales": f"{self.stock_info.get('priceToSalesTrailing12Months', 0):.2f}",
        }

    def get_profitability_metrics(self) -> dict:
        """Get profitability metrics"""
        return {
            "Gross Margin": self.format_percentage(self.stock_info.get('grossMargins')),
            "Operating Margin": self.format_percentage(self.stock_info.get('operatingMargins')),
            "Profit Margin": self.format_percentage(self.stock_info.get('profitMargins')),
            "ROE": self.format_percentage(self.stock_info.get('returnOnEquity')),
            "ROA": self.format_percentage(self.stock_info.get('returnOnAssets')),
        }

    def get_dividend_metrics(self) -> dict:
        """Get dividend metrics"""
        return {
            "Dividend Rate": self.format_currency(self.stock_info.get('dividendRate')),
            "Dividend Yield": self.format_percentage(self.stock_info.get('dividendYield')),
            "Payout Ratio": self.format_percentage(self.stock_info.get('payoutRatio')),
            "5Y Avg Dividend Yield": self.format_percentage(self.stock_info.get('fiveYearAvgDividendYield')),
        }

def display_financial_metrics(stock_info: dict):
    """Display comprehensive financial metrics"""
    analyzer = FinancialAnalyzer(stock_info)
    
    st.header("Financial Analysis")
    
    # Currency indicator
    st.caption(f"All monetary values in {analyzer.currency_symbol} ({['USD', 'THB'][analyzer.is_thai]})")
    
    # Income Statement Metrics
    st.subheader("Income Statement Metrics")
    metrics = analyzer.get_income_statement_metrics()
    cols = st.columns(4)
    for i, (metric, value) in enumerate(metrics.items()):
        with cols[i % 4]:
            st.metric(metric, value)
    
    # Balance Sheet Metrics
    st.subheader("Balance Sheet Metrics")
    metrics = analyzer.get_balance_sheet_metrics()
    cols = st.columns(3)
    for i, (metric, value) in enumerate(metrics.items()):
        with cols[i % 3]:
            st.metric(metric, value)
    
    # Display metrics in tabs
    tab1, tab2, tab3 = st.tabs(["Valuation", "Profitability", "Dividends"])
    
    with tab1:
        metrics = analyzer.get_valuation_metrics()
        cols = st.columns(4)
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 4]:
                st.metric(metric, value)
    
    with tab2:
        metrics = analyzer.get_profitability_metrics()
        cols = st.columns(3)
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 3]:
                st.metric(metric, value)
    
    with tab3:
        metrics = analyzer.get_dividend_metrics()
        cols = st.columns(3)
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 3]:
                st.metric(metric, value)

    # Create financial charts
    create_financial_charts(analyzer)

def create_financial_charts(analyzer: FinancialAnalyzer):
    """Create financial analysis charts"""
    st.subheader("Financial Metrics Visualization")
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Profitability Margins",
            "Returns Analysis",
            "Valuation Metrics",
            "Growth Analysis"
        )
    )
    
    # Profitability Margins
    margins = {
        'Gross Margin': analyzer.stock_info.get('grossMargins', 0),
        'Operating Margin': analyzer.stock_info.get('operatingMargins', 0),
        'Profit Margin': analyzer.stock_info.get('profitMargins', 0)
    }
    
    fig.add_trace(
        go.Bar(
            x=list(margins.keys()),
            y=[v*100 for v in margins.values()],
            name='Margins',
            marker_color='#2196F3'
        ),
        row=1, col=1
    )
    
    # Returns
    returns = {
        'ROE': analyzer.stock_info.get('returnOnEquity', 0),
        'ROA': analyzer.stock_info.get('returnOnAssets', 0)
    }
    
    fig.add_trace(
        go.Bar(
            x=list(returns.keys()),
            y=[v*100 for v in returns.values()],
            name='Returns',
            marker_color='#4CAF50'
        ),
        row=1, col=2
    )
    
    # Valuation Metrics
    valuation = {
        'P/E': analyzer.stock_info.get('trailingPE', 0),
        'Forward P/E': analyzer.stock_info.get('forwardPE', 0),
        'PEG': analyzer.stock_info.get('pegRatio', 0)
    }
    
    fig.add_trace(
        go.Bar(
            x=list(valuation.keys()),
            y=list(valuation.values()),
            name='Valuation',
            marker_color='#9C27B0'
        ),
        row=2, col=1
    )
    
    # Growth
    growth = {
        'Revenue Growth': analyzer.stock_info.get('revenueGrowth', 0),
        'Earnings Growth': analyzer.stock_info.get('earningsGrowth', 0)
    }
    
    fig.add_trace(
        go.Bar(
            x=list(growth.keys()),
            y=[v*100 for v in growth.values()],
            name='Growth',
            marker_color='#FF9800'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Financial Metrics Analysis"
    )
    
    # Update axes
    fig.update_yaxes(title_text="Percentage (%)", row=1, col=1)
    fig.update_yaxes(title_text="Percentage (%)", row=1, col=2)
    fig.update_yaxes(title_text="Ratio", row=2, col=1)
    fig.update_yaxes(title_text="Percentage (%)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    # Test with sample data
    sample_stock = {'symbol': 'PTT.BK', 'marketCap': 1000000000}
    display_financial_metrics(sample_stock)