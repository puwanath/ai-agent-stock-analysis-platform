"""
AI Analysis Component using Local LLMs
"""

import streamlit as st
import requests
import json
import asyncio
from datetime import datetime
from typing import Dict, Optional
import pandas as pd
from utils.thai_stock_fetcher import is_thai_stock

class AIAnalyzer:
    def __init__(self, config: Dict):
        """
        Initialize AI Analyzer with configuration
        
        Args:
            config: Configuration dictionary with AI settings
        """
        self.enabled = config.get('ai_analysis', {}).get('enabled', False)
        self.api_url = config.get('ai_analysis', {}).get('api_url', 'http://localhost:11434/api/generate')
        self.model = config.get('ai_analysis', {}).get('model', 'llama3.1:latest')
        self.timeout = config.get('ai_analysis', {}).get('timeout', 60)

    async def analyze_stock(
        self,
        stock_info: Dict,
        stock_data: pd.DataFrame,
        technical_indicators: Dict,
        financial_metrics: Dict
    ) -> Optional[Dict]:
        """
        Analyze stock data using local LLM
        
        Args:
            stock_info: Stock information
            stock_data: Historical price data
            technical_indicators: Technical analysis indicators
            financial_metrics: Financial metrics
            
        Returns:
            Dictionary with AI analysis or None if disabled/error
        """
        if not self.enabled:
            return None

        try:
            # Prepare analysis context
            is_thai = is_thai_stock(stock_info.get('symbol', ''))
            currency = 'THB' if is_thai else 'USD'
            current_price = stock_info.get('currentPrice', 0)
            
            prompt = f"""
            Analyze this stock and provide investment recommendation:
            
            Stock Information:
            - Symbol: {stock_info.get('symbol')}
            - Company: {stock_info.get('longName')}
            - Current Price: {currency} {current_price:,.2f}
            - Market Cap: {currency} {stock_info.get('marketCap', 0)/1e9:.2f}B
            - Sector: {stock_info.get('sector')}
            - Industry: {stock_info.get('industry')}
            
            Technical Analysis:
            - RSI: {technical_indicators.get('RSI', 'N/A')}
            - MACD: {technical_indicators.get('MACD', 'N/A')}
            - Moving Averages: {technical_indicators.get('MA_Status', 'N/A')}
            - Bollinger Bands: {technical_indicators.get('BB_Status', 'N/A')}
            
            Financial Metrics:
            - P/E Ratio: {stock_info.get('trailingPE', 'N/A')}
            - EPS: {stock_info.get('trailingEps', 'N/A')}
            - Profit Margin: {stock_info.get('profitMargins', 0) * 100:.1f}%
            - ROE: {stock_info.get('returnOnEquity', 0) * 100:.1f}%
            - Debt/Equity: {stock_info.get('debtToEquity', 'N/A')}
            
            Analyst Recommendations:
            - Target Price: {currency} {stock_info.get('targetMeanPrice', 'N/A')}
            - Recommendation: {stock_info.get('recommendationKey', 'N/A')}
            
            Please provide:
            1. Clear BUY, SELL, or HOLD recommendation with confidence level (high/medium/low)
            2. Key factors supporting the recommendation
            3. Key risks to consider
            4. Potential catalysts to watch
            5. Price targets (support and resistance levels)

            Please provide a detailed analysis in a clear and concise manner.
            Response Thai language.
            """

            # Call Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                analysis = response.json().get('response', '')
                return self._parse_analysis(analysis)
            else:
                st.error(f"Error from Ollama API: {response.status_code}")
                return None

        except Exception as e:
            st.error(f"Error in AI analysis: {str(e)}")
            return None

    def _parse_analysis(self, analysis: str) -> Dict:
        """Parse and structure the AI analysis response"""
        # Basic parsing of the analysis text
        recommendation = "HOLD"  # Default
        confidence = "low"
        
        analysis_lower = analysis.lower()
        if "buy" in analysis_lower:
            recommendation = "BUY"
        elif "sell" in analysis_lower:
            recommendation = "SELL"
        
        if "high confidence" in analysis_lower:
            confidence = "high"
        elif "medium confidence" in analysis_lower:
            confidence = "medium"

        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'full_analysis': analysis,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def display_ai_analysis(
    stock_info: Dict,
    stock_data: pd.DataFrame,
    technical_indicators: Dict,
    financial_metrics: Dict,
    config: Dict
):
    """Display AI analysis section"""
    st.header("AI Analysis")
    
    if not config.get('ai_analysis', {}).get('enabled', False):
        st.info("AI analysis is disabled. Enable it in configuration to view AI-powered recommendations.")
        return

    analyzer = AIAnalyzer(config)
    
    # with st.spinner("Analyzing data using AI..."):
    #     analysis = analyzer.analyze_stock(
    #         stock_info,
    #         stock_data,
    #         technical_indicators,
    #         financial_metrics
    #     )
    with st.spinner("Analyzing data using AI..."):
        # Create event loop and run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            analysis = loop.run_until_complete(
                analyzer.analyze_stock(
                    stock_info,
                    stock_data,
                    technical_indicators,
                    financial_metrics
                )
            )
        finally:
            loop.close()
        
    if analysis:
        # Display recommendation
        recommendation = analysis['recommendation']
        confidence = analysis['confidence']
        
        # Style based on recommendation
        # if recommendation == "BUY":
        #     st.success(f"🔔 AI Recommendation: **{recommendation}** (Confidence: {confidence.upper()})")
        # elif recommendation == "SELL":
        #     st.error(f"🔔 AI Recommendation: **{recommendation}** (Confidence: {confidence.upper()})")
        # else:
        #     st.warning(f"🔔 AI Recommendation: **{recommendation}** (Confidence: {confidence.upper()})")
        
        if recommendation == "BUY":
            st.success(f"🔔 AI Recommendation: **{recommendation}**")
        elif recommendation == "SELL":
            st.error(f"🔔 AI Recommendation: **{recommendation}**")
        else:
            st.warning(f"🔔 AI Recommendation: **{recommendation}**")

        # Display full analysis in expandable section
        with st.expander("View Detailed Analysis", expanded=True):
            st.markdown(analysis['full_analysis'])
            
        st.caption(f"Analysis generated at: {analysis['timestamp']}")
        
        # Disclaimer
        st.warning("""
        **Disclaimer**: This AI-generated analysis is for informational purposes only. 
        Always conduct your own research and consult with a financial advisor before making investment decisions.
        """)
    else:
        st.error("Unable to generate AI analysis. Please try again later.")