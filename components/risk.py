import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from scipy import stats
from datetime import datetime, timedelta

class RiskAnalyzer:
    def __init__(self, df, stock_info=None, benchmark_symbol='SPY'):
        """
        Initialize RiskAnalyzer with stock data and optional benchmark
        
        Args:
            df: DataFrame with OHLCV data
            stock_info: Dictionary containing stock information
            benchmark_symbol: Symbol for benchmark comparison (default: 'SPY')
        """
        self.df = df
        self.stock_info = stock_info
        self.benchmark_symbol = benchmark_symbol
        self.risk_metrics = {}
        self.calculate_risk_metrics()

    def calculate_risk_metrics(self):
        """Calculate various risk metrics"""
        # Calculate returns
        self.df['Returns'] = self.df['Close'].pct_change()
        
        # Basic risk metrics
        self.risk_metrics['daily_volatility'] = self.df['Returns'].std()
        self.risk_metrics['annual_volatility'] = self.risk_metrics['daily_volatility'] * np.sqrt(252)
        self.risk_metrics['sharpe_ratio'] = self.calculate_sharpe_ratio()
        self.risk_metrics['sortino_ratio'] = self.calculate_sortino_ratio()
        self.risk_metrics['max_drawdown'] = self.calculate_max_drawdown()
        self.risk_metrics['var_95'] = self.calculate_var(0.95)
        self.risk_metrics['cvar_95'] = self.calculate_cvar(0.95)
        self.risk_metrics['beta'] = self.calculate_beta()
        
        # Additional metrics
        self.risk_metrics['skewness'] = self.df['Returns'].skew()
        self.risk_metrics['kurtosis'] = self.df['Returns'].kurtosis()
        self.risk_metrics['downside_deviation'] = self.calculate_downside_deviation()

    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """Calculate Sharpe Ratio"""
        excess_returns = self.df['Returns'].mean() * 252 - risk_free_rate
        return excess_returns / (self.df['Returns'].std() * np.sqrt(252))

    def calculate_sortino_ratio(self, risk_free_rate=0.02):
        """Calculate Sortino Ratio"""
        excess_returns = self.df['Returns'].mean() * 252 - risk_free_rate
        downside_deviation = self.calculate_downside_deviation()
        return excess_returns / (downside_deviation * np.sqrt(252))

    def calculate_max_drawdown(self):
        """Calculate Maximum Drawdown"""
        cumulative_returns = (1 + self.df['Returns']).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns/rolling_max - 1
        return drawdowns.min()

    def calculate_var(self, confidence_level):
        """Calculate Value at Risk"""
        return np.percentile(self.df['Returns'], (1-confidence_level)*100)

    def calculate_cvar(self, confidence_level):
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = self.calculate_var(confidence_level)
        return self.df['Returns'][self.df['Returns'] <= var].mean()

    def calculate_beta(self):
        """Calculate Beta relative to benchmark"""
        try:
            benchmark = yf.download(
                self.benchmark_symbol,
                start=self.df.index[0],
                end=self.df.index[-1],
                progress=False
            )
            benchmark_returns = benchmark['Close'].pct_change()
            covariance = np.cov(self.df['Returns'].dropna(), benchmark_returns.dropna())[0,1]
            benchmark_variance = np.var(benchmark_returns.dropna())
            return covariance / benchmark_variance
        except:
            return None

    def calculate_downside_deviation(self, target_return=0):
        """Calculate Downside Deviation"""
        negative_returns = self.df['Returns'][self.df['Returns'] < target_return]
        return np.sqrt(np.mean(negative_returns**2))

    def plot_risk_metrics(self):
        """Create visualization of risk metrics"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Returns Distribution',
                'Rolling Volatility',
                'Drawdown Analysis',
                'Value at Risk'
            )
        )

        # Returns Distribution
        fig.add_trace(
            go.Histogram(
                x=self.df['Returns'],
                name='Returns',
                nbinsx=50,
                histnorm='probability'
            ),
            row=1, col=1
        )

        # Rolling Volatility
        rolling_vol = self.df['Returns'].rolling(window=21).std() * np.sqrt(252)
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=rolling_vol,
                name='21-Day Rolling Volatility'
            ),
            row=1, col=2
        )

        # Drawdown Analysis
        cumulative_returns = (1 + self.df['Returns']).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns/rolling_max - 1
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=drawdowns,
                name='Drawdown',
                fill='tonexty'
            ),
            row=2, col=1
        )

        # Value at Risk
        returns_sorted = sorted(self.df['Returns'].dropna())
        var_95 = self.risk_metrics['var_95']
        fig.add_trace(
            go.Scatter(
                x=returns_sorted,
                y=np.linspace(0, 1, len(returns_sorted)),
                name='Returns CDF'
            ),
            row=2, col=2
        )
        fig.add_vline(
            x=var_95,
            line_dash="dash",
            annotation_text=f"95% VaR: {var_95:.2%}",
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Risk Analysis Dashboard"
        )

        return fig

class RiskAssessment:
    @staticmethod
    def get_risk_rating(metrics):
        """
        Get overall risk rating based on various metrics
        Returns: (rating, explanation)
        """
        annual_vol = metrics['annual_volatility']
        beta = metrics['beta']
        max_drawdown = metrics['max_drawdown']
        
        # Base risk score
        risk_score = 0
        reasons = []

        # Volatility assessment
        if annual_vol > 0.40:
            risk_score += 3
            reasons.append("Very high volatility")
        elif annual_vol > 0.25:
            risk_score += 2
            reasons.append("High volatility")
        elif annual_vol > 0.15:
            risk_score += 1
            reasons.append("Moderate volatility")

        # Beta assessment
        if beta is not None:
            if beta > 1.5:
                risk_score += 3
                reasons.append("Very high market sensitivity")
            elif beta > 1.2:
                risk_score += 2
                reasons.append("High market sensitivity")
            elif beta > 1:
                risk_score += 1
                reasons.append("Above-market sensitivity")

        # Drawdown assessment
        if max_drawdown < -0.50:
            risk_score += 3
            reasons.append("Severe historical drawdowns")
        elif max_drawdown < -0.30:
            risk_score += 2
            reasons.append("Significant historical drawdowns")
        elif max_drawdown < -0.20:
            risk_score += 1
            reasons.append("Moderate historical drawdowns")

        # Determine final rating
        if risk_score >= 7:
            rating = "Very High Risk"
        elif risk_score >= 5:
            rating = "High Risk"
        elif risk_score >= 3:
            rating = "Moderate Risk"
        else:
            rating = "Low Risk"

        return rating, reasons

def display_risk_metrics(df, stock_info=None):
    """Display comprehensive risk analysis"""
    st.header("Risk Analysis")

    # Initialize risk analyzer
    risk_analyzer = RiskAnalyzer(df, stock_info)
    
    # Get risk rating
    risk_rating, risk_reasons = RiskAssessment.get_risk_rating(risk_analyzer.risk_metrics)

    # Display risk rating
    st.subheader("Risk Rating")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Overall Risk Rating", risk_rating)
    with col2:
        st.markdown("**Key Risk Factors:**")
        for reason in risk_reasons:
            st.markdown(f"• {reason}")

    # Display key risk metrics
    st.subheader("Key Risk Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Annual Volatility",
            f"{risk_analyzer.risk_metrics['annual_volatility']*100:.1f}%"
        )
    with col2:
        st.metric(
            "Beta",
            f"{risk_analyzer.risk_metrics['beta']:.2f}" if risk_analyzer.risk_metrics['beta'] else "N/A"
        )
    with col3:
        st.metric(
            "Maximum Drawdown",
            f"{risk_analyzer.risk_metrics['max_drawdown']*100:.1f}%"
        )
    with col4:
        st.metric(
            "Value at Risk (95%)",
            f"{risk_analyzer.risk_metrics['var_95']*100:.1f}%"
        )

    # Display risk analysis charts
    st.plotly_chart(risk_analyzer.plot_risk_metrics(), use_container_width=True)

    # Additional risk metrics
    st.subheader("Additional Risk Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sharpe Ratio", f"{risk_analyzer.risk_metrics['sharpe_ratio']:.2f}")
        st.metric("Sortino Ratio", f"{risk_analyzer.risk_metrics['sortino_ratio']:.2f}")
    
    with col2:
        st.metric("Skewness", f"{risk_analyzer.risk_metrics['skewness']:.2f}")
        st.metric("Kurtosis", f"{risk_analyzer.risk_metrics['kurtosis']:.2f}")
    
    with col3:
        st.metric("CVaR (95%)", f"{risk_analyzer.risk_metrics['cvar_95']*100:.1f}%")
        st.metric(
            "Downside Deviation",
            f"{risk_analyzer.risk_metrics['downside_deviation']*100:.1f}%"
        )

    # Risk interpretation
    with st.expander("Risk Metrics Explanation"):
        st.markdown("""
        **Key Risk Metrics Explained:**
        - **Volatility:** Measures price variation/risk (higher = more volatile)
        - **Beta:** Stock's sensitivity to market movements (>1 = more sensitive)
        - **Maximum Drawdown:** Largest peak-to-trough decline
        - **Value at Risk:** Maximum likely loss at 95% confidence level
        - **Sharpe Ratio:** Risk-adjusted return (higher = better)
        - **Sortino Ratio:** Downside risk-adjusted return
        - **Skewness:** Return distribution symmetry
        - **Kurtosis:** Frequency of extreme returns
        - **CVaR:** Average loss beyond VaR
        - **Downside Deviation:** Volatility of negative returns only
        """)

def display_trading_signals(stock_data):
    """Display trading signals with proper data validation"""
    if stock_data is None or stock_data.empty:
        st.warning("No trading data available")
        return
        
    # Calculate volume metrics
    short_vol = stock_data['Volume'].rolling(window=20).mean()
    long_vol = stock_data['Volume'].rolling(window=50).mean()
    
    # Get current values with safe indexing
    if len(short_vol) > 0:
        current_vol = short_vol.iloc[-1]
        avg_vol = long_vol.iloc[-1]
        
        # Display volume analysis
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Volume MA (20)", f"{current_vol:,.0f}")
        with col2:
            st.metric("Average Volume MA (50)", f"{avg_vol:,.0f}")
            
        # Generate trading signals
        if current_vol > avg_vol * 1.5:
            st.info("📈 High volume detected - potential breakout signal")
        elif current_vol < avg_vol * 0.5:
            st.info("📉 Low volume detected - potential consolidation")

if __name__ == "__main__":
    # Test with sample data
    symbol = "AAPL"
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1y")
    stock_info = ticker.info
    
    display_risk_metrics(df, stock_info)
    display_trading_signals(df)