"""
AI-Agents Stock Analyst Platform
"""

import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime

# Configure Streamlit page - must be the first Streamlit command
st.set_page_config(
    page_title="AI-Agents Stock Analyst Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config.settings import Settings
from utils.data_fetcher import get_data_fetcher
from utils.thai_stock_fetcher import ThaiStockFetcher, is_thai_stock
from utils.technical_indicators import get_technical_indicators, interpret_indicators
from utils.financial_metrics import get_financial_metrics, interpret_financial_metrics

# Import components
from components.company_info import display_company_info
from components.technical import display_technical_analysis
from components.financial import display_financial_metrics
from components.news import display_news_section
from components.risk import display_risk_metrics, display_trading_signals
from components.charts import display_chart_analysis
from components.research import display_research_analysis
from components.ai_analyzer import display_ai_analysis

# Default configuration
DEFAULT_CONFIG = {
    'ai_analysis': {
        'enabled': True,
        'api_url': 'http://localhost:11434/api/generate',
        'model': 'llama3.1:latest',
        'timeout': 60
    }
}

# Initialize settings
settings = Settings()
config = settings.get_all_settings()

# Custom CSS for fixed header
st.markdown("""
    <style>
        div[data-testid="stHeader"] {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background-color: #0e1117;
            padding: 1rem;
        }
        .main > div {
            padding-top: 5rem;
        }
        .block-container {
            padding-top: 2rem;
        }
        #MainMenu {visibility: visible;}
        header {visibility: visible;}
        header[data-testid="stHeader"] {
            background-color: rgba(14, 17, 23, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .stApp header {
            background-color: transparent;
        }
        /* Custom styling for sidebar */
        .css-1d391kg {
            padding-top: 3.5rem;
        }
        /* Improve input field appearance */
        .stTextInput input {
            border-radius: 0.5rem;
        }
        /* Style the analyze button */
        .stButton button {
            width: 100%;
            border-radius: 0.5rem;
            transition: all 0.3s;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'data_fetcher' not in st.session_state:
        st.session_state['data_fetcher'] = None
    if 'thai_fetcher' not in st.session_state:
        st.session_state['thai_fetcher'] = ThaiStockFetcher()
    if 'current_symbol' not in st.session_state:
        st.session_state['current_symbol'] = None
    if 'stock_data' not in st.session_state:
        st.session_state['stock_data'] = None
    if 'stock_info' not in st.session_state:
        st.session_state['stock_info'] = None
    if 'is_thai' not in st.session_state:
        st.session_state['is_thai'] = False
    if 'config' not in st.session_state:
        st.session_state['config'] = DEFAULT_CONFIG

async def load_data(symbol: str, period: str = "1y"):
    """Load stock data asynchronously"""
    is_thai = is_thai_stock(symbol)
    st.session_state['is_thai'] = is_thai
    
    if is_thai:
        if not st.session_state['thai_fetcher']:
            st.session_state['thai_fetcher'] = ThaiStockFetcher()
        df, info = await st.session_state['thai_fetcher'].fetch_stock_data(symbol, period)
    else:
        if not st.session_state['data_fetcher']:
            st.session_state['data_fetcher'] = await get_data_fetcher()
        df, info = await st.session_state['data_fetcher'].fetch_stock_data(symbol, period)
    
    return df, info

def show_loading_message():
    """Display loading spinner with message"""
    with st.spinner('Fetching and analyzing data... Please wait.'):
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
        progress_bar.empty()

def main():
    # Initialize session state
    initialize_session_state()
    
    # Fixed header
    with st.container():
        # col1, col2 = st.columns([2,1])
        # with col1:
        st.title("AI-Agents Stock Analyst Platform")
        st.caption("Professional-grade stock analysis powered by AI #Developer by 9kapong.Dev#")
            
    
    # Sidebar controls
    st.sidebar.header("Configuration")
    
    # Text input for stock symbol
    symbol = st.sidebar.text_input(
        "Enter Stock Symbol", 
        placeholder="e.g., AAPL, PTT.BK",
        help="For Thai stocks, you can enter with or without .BK (e.g., PTT or PTT.BK)"
    ).upper()
    
    if not symbol:
        st.info("👈 Please enter a stock symbol in the sidebar to begin analysis")
        
        # Show some example stocks or featured analysis
        st.subheader("Popular Stocks")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("AAPL - Apple Inc.")
        with col2:
            st.button("MSFT - Microsoft")
        with col3:
            st.button("PTT.BK - PTT Public")
        
        return
    
    # Time period selection
    period_options = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
    period = st.sidebar.selectbox(
        "Select Time Period",
        options=period_options,
        index=period_options.index("1y")
    )

    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type",
        ["Overview", "Research Analysis", "Technical Analysis", "Financial Analysis", 
         "Risk Analysis", "News & Sentiment"]
    )

    # Add AI Analysis toggle to sidebar
    st.sidebar.header("AI Analysis Settings")
    enable_ai = st.sidebar.checkbox(
        "Enable AI Analysis",
        value=config.get('ai_analysis', {}).get('enabled', False),
        help="Use AI to analyze stock data and provide recommendations"
    )
    # Update config with user preference
    st.session_state['config']['ai_analysis']['enabled'] = enable_ai
    
    # Technical indicators selection
    if analysis_type == "Technical Analysis":
        st.sidebar.subheader("Technical Indicators")
        show_ma = st.sidebar.checkbox("Moving Averages", True)
        show_bb = st.sidebar.checkbox("Bollinger Bands", True)
        show_rsi = st.sidebar.checkbox("RSI", True)
        show_macd = st.sidebar.checkbox("MACD", True)

    # Load data button
    if st.sidebar.button("Analyze", type="primary"):
        show_loading_message()
        df, info = asyncio.run(load_data(symbol, period))
        st.session_state['stock_data'] = df
        st.session_state['stock_info'] = info
        st.session_state['current_symbol'] = symbol

    # Display analysis based on selection
    if st.session_state.get('stock_data') is not None and st.session_state.get('stock_info') is not None:
         # Calculate technical indicators
        technical_indicators = get_technical_indicators(st.session_state['stock_data'])
        financial_metrics = get_financial_metrics(st.session_state['stock_info'])
        
        if analysis_type == "Overview":
             # Company Overview
            display_company_info(st.session_state['stock_info'])
             # AI Analysis (if enabled)
            if enable_ai:
                display_ai_analysis(
                    st.session_state['stock_info'],
                    st.session_state['stock_data'],
                    technical_indicators,
                    financial_metrics,
                    st.session_state['config']
                )

            # Others sections
            display_research_analysis(st.session_state['stock_info']) 
            display_trading_signals(st.session_state['stock_data'])
            display_chart_analysis(st.session_state['stock_data'])
        elif analysis_type == "Research Analysis":
            display_research_analysis(st.session_state['stock_info'])
        elif analysis_type == "Technical Analysis":
            display_technical_analysis(st.session_state['stock_data'])
        elif analysis_type == "Financial Analysis":
            display_financial_metrics(st.session_state['stock_info'])
        elif analysis_type == "Risk Analysis":
            display_risk_metrics(st.session_state['stock_data'], st.session_state['stock_info'])
        elif analysis_type == "News & Sentiment":
            display_news_section(symbol)

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center'>
            <p>Powered by AI-Agents Stock Analyst | Data provided by Yahoo Finance</p>
            <p>Last updated: {}</p>
        </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")