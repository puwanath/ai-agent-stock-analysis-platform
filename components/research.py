"""
Research Analysis Component
Handles research metrics, earnings analysis, and analyst recommendations
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.thai_stock_fetcher import is_thai_stock

class ResearchAnalyzer:
    def __init__(self, stock_info: dict):
        self.stock_info = stock_info
        self.symbol = stock_info.get('symbol', '')
        self.is_thai = is_thai_stock(self.symbol)
        self.currency = '฿' if self.is_thai else '$'

    def format_currency(self, value: float, precision: int = 2) -> str:
        if pd.isna(value) or value is None:
            return 'N/A'
        return f"{self.currency}{value:,.{precision}f}"

    def create_eps_chart(self) -> go.Figure:
        """Create EPS trend chart"""
        fig = go.Figure()

        # Get EPS data
        trailing_eps = self.stock_info.get('trailingEps', 0)
        forward_eps = self.stock_info.get('forwardEps', 0)

        fig.add_trace(go.Bar(
            x=['Trailing EPS', 'Forward EPS'],
            y=[trailing_eps, forward_eps],
            text=[self.format_currency(trailing_eps), self.format_currency(forward_eps)],
            textposition='auto',
            marker_color=['#1f77b4', '#2ca02c']
        ))

        fig.update_layout(
            title='EPS Analysis',
            yaxis_title='EPS Value',
            height=400,
            showlegend=False
        )

        return fig

    def create_revenue_earnings_chart(self) -> go.Figure:
        """Create revenue vs earnings chart"""
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Get financial data
        revenue = self.stock_info.get('totalRevenue', 0)
        earnings = self.stock_info.get('netIncomeToCommon', 0)

        # Add Revenue bar
        fig.add_trace(
            go.Bar(
                name='Revenue',
                x=['Latest Period'],
                y=[revenue],
                text=[self.format_currency(revenue/1e9) + 'B'],
                textposition='auto',
                marker_color='#1f77b4'
            ),
            secondary_y=False
        )

        # Add Earnings bar
        fig.add_trace(
            go.Bar(
                name='Earnings',
                x=['Latest Period'],
                y=[earnings],
                text=[self.format_currency(earnings/1e9) + 'B'],
                textposition='auto',
                marker_color='#2ca02c'
            ),
            secondary_y=False
        )

        fig.update_layout(
            title='Revenue vs. Earnings',
            height=400,
            barmode='group'
        )

        return fig

def display_research_analysis(stock_info: dict):
    """Display comprehensive research analysis"""
    analyzer = ResearchAnalyzer(stock_info)

    # Section 1: Earnings Per Share Analysis
    st.subheader("Earnings Per Share (EPS) Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Trailing EPS",
            analyzer.format_currency(stock_info.get('trailingEps')),
            help="Previous 12 months earnings per share"
        )
    with col2:
        st.metric(
            "Forward EPS",
            analyzer.format_currency(stock_info.get('forwardEps')),
            help="Projected next 12 months earnings per share"
        )
    with col3:
        eps_growth = ((stock_info.get('forwardEps', 0) - stock_info.get('trailingEps', 0)) 
                     / abs(stock_info.get('trailingEps', 1)) * 100)
        st.metric(
            "EPS Growth",
            f"{eps_growth:.1f}%",
            help="Expected EPS growth"
        )

    # EPS Chart
    st.plotly_chart(analyzer.create_eps_chart(), use_container_width=True)

    # Section 2: Revenue vs. Earnings
    st.subheader("Revenue vs. Earnings Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Revenue",
            analyzer.format_currency(stock_info.get('totalRevenue')/1e9) + 'B',
            help="Total revenue"
        )
    with col2:
        st.metric(
            "Net Income",
            analyzer.format_currency(stock_info.get('netIncomeToCommon')/1e9) + 'B',
            help="Net income"
        )
    with col3:
        profit_margin = stock_info.get('profitMargins', 0) * 100
        st.metric(
            "Profit Margin",
            f"{profit_margin:.1f}%",
            help="Profit margin percentage"
        )

    # Revenue vs Earnings Chart
    st.plotly_chart(analyzer.create_revenue_earnings_chart(), use_container_width=True)

    # Section 3: Analyst Recommendations
    st.subheader("Analyst Recommendations")
    
    recommendations = {
        'strongBuy': stock_info.get('recommendationKey', 'N/A'),
        'targetHigh': stock_info.get('targetHighPrice', 0),
        'targetMean': stock_info.get('targetMeanPrice', 0),
        'targetLow': stock_info.get('targetLowPrice', 0),
        'numberOfAnalysts': stock_info.get('numberOfAnalysts', 0)
    }
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Recommendation",
            recommendations['strongBuy'].upper(),
            help="Overall analyst recommendation"
        )
    with col2:
        st.metric(
            "Target High",
            analyzer.format_currency(recommendations['targetHigh']),
            help="Highest analyst price target"
        )
    with col3:
        st.metric(
            "Target Mean",
            analyzer.format_currency(recommendations['targetMean']),
            help="Average analyst price target"
        )
    with col4:
        st.metric(
            "Target Low",
            analyzer.format_currency(recommendations['targetLow']),
            help="Lowest analyst price target"
        )

    # Additional analyst info
    st.caption(f"Based on {recommendations['numberOfAnalysts']} analyst recommendations")

    # Create price target chart
    current_price = stock_info.get('currentPrice', 0)
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "gauge+number",
        value = current_price,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [recommendations['targetLow'], recommendations['targetHigh']]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [recommendations['targetLow'], recommendations['targetMean']], 'color': "lightgray"},
                {'range': [recommendations['targetMean'], recommendations['targetHigh']], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': recommendations['targetMean']
            }
        },
        title = {'text': "Current Price vs. Price Targets"}
    ))

    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)