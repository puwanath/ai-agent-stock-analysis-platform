import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class ChartCreator:
    def __init__(self, df, stock_info=None):
        """Initialize chart creator with dataframe and stock info"""
        self.df = df
        self.stock_info = stock_info
        self.theme = 'plotly_dark'
        self.default_colors = {
            'up': '#26a69a',      # Green for upward movement
            'down': '#ef5350',     # Red for downward movement
            'line': '#1e88e5',     # Blue for lines
            'volume': '#90a4ae',   # Grey for volume
            'band': 'rgba(128, 128, 128, 0.2)'  # Semi-transparent grey for bands
        }

    def create_candlestick_chart(self, include_volume=True):
        """Create a candlestick chart with optional volume"""
        fig = make_subplots(
            rows=2 if include_volume else 1,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3] if include_volume else [1]
        )

        # Add candlestick
        fig.add_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['Open'],
                high=self.df['High'],
                low=self.df['Low'],
                close=self.df['Close'],
                name='OHLC',
                increasing_line_color=self.default_colors['up'],
                decreasing_line_color=self.default_colors['down']
            ),
            row=1, col=1
        )

        # Add volume bars if requested
        if include_volume:
            colors = [self.default_colors['up'] if c >= o else self.default_colors['down']
                     for c, o in zip(self.df['Close'], self.df['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=self.df.index,
                    y=self.df['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.8
                ),
                row=2, col=1
            )

        # Update layout
        fig.update_layout(
            title='Price and Volume Analysis',
            yaxis_title='Price',
            yaxis2_title='Volume' if include_volume else None,
            xaxis_rangeslider_visible=False,
            template=self.theme,
            height=800,
            showlegend=False
        )

        return fig

    def create_technical_chart(self, indicators=None):
        """Create a technical analysis chart with specified indicators"""
        if indicators is None:
            indicators = {'ma': True, 'bb': True, 'volume': True, 'macd': True, 'rsi': True}

        # Calculate number of rows needed
        num_rows = 1 + sum([indicators.get('volume', False),
                           indicators.get('macd', False),
                           indicators.get('rsi', False)])

        # Create subplots
        fig = make_subplots(
            rows=num_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5] + [0.25] * (num_rows - 1)
        )

        # Main price chart
        fig.add_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['Open'],
                high=self.df['High'],
                low=self.df['Low'],
                close=self.df['Close'],
                name='OHLC'
            ),
            row=1, col=1
        )

        current_row = 1
        
        # Add Moving Averages
        if indicators.get('ma'):
            for period in [20, 50, 200]:
                if f'MA{period}' in self.df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=self.df.index,
                            y=self.df[f'MA{period}'],
                            name=f'{period}MA',
                            line=dict(width=1)
                        ),
                        row=1, col=1
                    )

        # Add Bollinger Bands
        if indicators.get('bb'):
            for band in ['upper', 'middle', 'lower']:
                if f'BB_{band}' in self.df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=self.df.index,
                            y=self.df[f'BB_{band}'],
                            name=f'BB {band}',
                            line=dict(dash='dash')
                        ),
                        row=1, col=1
                    )

        # Add Volume
        if indicators.get('volume'):
            current_row += 1
            colors = [self.default_colors['up'] if c >= o else self.default_colors['down']
                     for c, o in zip(self.df['Close'], self.df['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=self.df.index,
                    y=self.df['Volume'],
                    name='Volume',
                    marker_color=colors
                ),
                row=current_row, col=1
            )

        # Add MACD
        if indicators.get('macd') and 'MACD' in self.df.columns:
            current_row += 1
            fig.add_trace(
                go.Scatter(
                    x=self.df.index,
                    y=self.df['MACD'],
                    name='MACD'
                ),
                row=current_row, col=1
            )
            if 'MACD_Signal' in self.df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df['MACD_Signal'],
                        name='Signal'
                    ),
                    row=current_row, col=1
                )

        # Add RSI
        if indicators.get('rsi') and 'RSI' in self.df.columns:
            current_row += 1
            fig.add_trace(
                go.Scatter(
                    x=self.df.index,
                    y=self.df['RSI'],
                    name='RSI'
                ),
                row=current_row, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=current_row, col=1)

        # Update layout
        fig.update_layout(
            title='Technical Analysis Chart',
            yaxis_title='Price',
            height=200 * num_rows,
            template=self.theme,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )

        return fig

    def create_correlation_chart(self, benchmark_symbol='SPY'):
        """Create correlation analysis chart with benchmark"""
        try:
            # Get benchmark data
            benchmark = yf.download(
                benchmark_symbol,
                start=self.df.index[0],
                end=self.df.index[-1],
                progress=False
            )

            # Normalize prices
            stock_normalized = self.df['Close'] / self.df['Close'].iloc[0]
            benchmark_normalized = benchmark['Close'] / benchmark['Close'].iloc[0]

            # Calculate correlation
            correlation = stock_normalized.corr(benchmark_normalized)

            fig = go.Figure()

            # Add stock line
            fig.add_trace(
                go.Scatter(
                    x=self.df.index,
                    y=stock_normalized,
                    name=self.stock_info.get('symbol', 'Stock') if self.stock_info else 'Stock',
                    line=dict(color=self.default_colors['line'])
                )
            )

            # Add benchmark line
            fig.add_trace(
                go.Scatter(
                    x=benchmark.index,
                    y=benchmark_normalized,
                    name=benchmark_symbol,
                    line=dict(color=self.default_colors['volume'])
                )
            )

            # Update layout
            fig.update_layout(
                title=f'Relative Performance Comparison (Correlation: {correlation:.2f})',
                yaxis_title='Normalized Price',
                height=500,
                template=self.theme,
                showlegend=True
            )

            return fig

        except Exception as e:
            st.error(f"Could not create correlation chart: {e}")
            return None

    def create_volume_profile(self, num_bins=100):
        """Create volume profile chart"""
        # Calculate price range and bins
        price_range = self.df['Close'].max() - self.df['Close'].min()
        bin_size = price_range / num_bins
        bins = np.linspace(self.df['Close'].min(), self.df['Close'].max(), num_bins)
        
        # Calculate volume for each price bin
        volume_profile = np.zeros(len(bins)-1)
        for i in range(len(self.df)):
            bin_idx = np.digitize(self.df['Close'].iloc[i], bins) - 1
            if 0 <= bin_idx < len(volume_profile):
                volume_profile[bin_idx] += self.df['Volume'].iloc[i]

        # Create figure
        fig = go.Figure()

        # Add volume profile
        fig.add_trace(
            go.Bar(
                x=volume_profile,
                y=[(bins[i] + bins[i+1])/2 for i in range(len(bins)-1)],
                orientation='h',
                name='Volume Profile',
                marker_color=self.default_colors['volume']
            )
        )

        # Add current price line
        fig.add_hline(
            y=self.df['Close'].iloc[-1],
            line_dash="dash",
            line_color=self.default_colors['line'],
            annotation_text="Current Price"
        )

        # Update layout
        fig.update_layout(
            title='Volume Profile Analysis',
            xaxis_title='Volume',
            yaxis_title='Price',
            height=800,
            template=self.theme,
            showlegend=False
        )

        return fig

    def create_fibonacci_chart(self):
        """Create Fibonacci retracement levels chart"""
        # Find high and low points
        high = self.df['High'].max()
        low = self.df['Low'].min()
        diff = high - low
        
        # Calculate Fibonacci levels
        levels = {
            '0.0': low,
            '0.236': low + 0.236 * diff,
            '0.382': low + 0.382 * diff,
            '0.5': low + 0.5 * diff,
            '0.618': low + 0.618 * diff,
            '0.786': low + 0.786 * diff,
            '1.0': high
        }

        fig = go.Figure()

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['Open'],
                high=self.df['High'],
                low=self.df['Low'],
                close=self.df['Close'],
                name='OHLC'
            )
        )

        # Add Fibonacci levels
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'violet']
        for (level, price), color in zip(levels.items(), colors):
            fig.add_hline(
                y=price,
                line_color=color,
                line_dash="dash",
                annotation_text=f"Fib {level}",
                annotation_position="left"
            )

        # Update layout
        fig.update_layout(
            title='Fibonacci Retracement Levels',
            yaxis_title='Price',
            height=800,
            template=self.theme,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )

        return fig

def display_chart_analysis(df, stock_info=None):
    """Main function to display all chart analyses"""
    chart_creator = ChartCreator(df, stock_info)

    # Sidebar options for chart customization
    st.sidebar.header("Chart Options")
    chart_type = st.sidebar.selectbox(
        "Select Chart Type",
        ["Basic Candlestick", "Technical Analysis", "Volume Profile", "Correlation", "Fibonacci"]
    )

    # Display selected chart
    if chart_type == "Basic Candlestick":
        include_volume = st.sidebar.checkbox("Include Volume", True)
        st.plotly_chart(chart_creator.create_candlestick_chart(include_volume), use_container_width=True)

    elif chart_type == "Technical Analysis":
        indicators = {
            'ma': st.sidebar.checkbox("Moving Averages", True),
            'bb': st.sidebar.checkbox("Bollinger Bands", True),
            'volume': st.sidebar.checkbox("Volume", True),
            'macd': st.sidebar.checkbox("MACD", True),
            'rsi': st.sidebar.checkbox("RSI", True)
        }
        st.plotly_chart(chart_creator.create_technical_chart(indicators), use_container_width=True)

    elif chart_type == "Volume Profile":
        num_bins = st.sidebar.slider("Number of Price Bins", 50, 200, 100)
        st.plotly_chart(chart_creator.create_volume_profile(num_bins), use_container_width=True)

    elif chart_type == "Correlation":
        benchmark = st.sidebar.text_input("Benchmark Symbol", "SPY")
        correlation_chart = chart_creator.create_correlation_chart(benchmark)
        if correlation_chart:
            st.plotly_chart(correlation_chart, use_container_width=True)

    elif chart_type == "Fibonacci":
        st.plotly_chart(chart_creator.create_fibonacci_chart(), use_container_width=True)

def display_all_charts(df, stock_info=None):
    """Display all chart analyses in a single view"""
    chart_creator = ChartCreator(df, stock_info)
    
    st.header("Comprehensive Chart Analysis")
    
    # Technical Analysis Chart
    st.subheader("Technical Analysis")
    st.plotly_chart(chart_creator.create_technical_chart(), use_container_width=True)
    
    # Volume Profile
    st.subheader("Volume Profile")
    st.plotly_chart(chart_creator.create_volume_profile(), use_container_width=True)
    
    # Correlation Analysis
    st.subheader("Market Correlation")
    correlation_chart = chart_creator.create_correlation_chart()
    if correlation_chart:
        st.plotly_chart(correlation_chart, use_container_width=True)
    
    # Fibonacci Analysis
    st.subheader("Fibonacci Retracement")
    st.plotly_chart(chart_creator.create_fibonacci_chart(), use_container_width=True)