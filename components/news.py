"""
News Analysis Component
Handles fetching and analyzing news articles for stocks
"""

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from textblob import TextBlob
from typing import List, Dict, Optional

class NewsAnalyzer:
    """Class for analyzing stock-related news"""
    
    def __init__(self, symbol: str):
        """
        Initialize NewsAnalyzer
        
        Args:
            symbol: Stock symbol
        """
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol) if symbol else None
        self.articles = []
        self.sentiment_scores = []
    
    def fetch_news(self, days_back: int = 30) -> bool:
        """
        Fetch news articles for the stock
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.ticker:
                return False
                
            self.articles = self.ticker.news
            
            if days_back and self.articles:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                self.articles = [
                    article for article in self.articles 
                    if datetime.fromtimestamp(article['providerPublishTime']) > cutoff_date
                ]
            
            # Pre-calculate sentiment for all articles
            for article in self.articles:
                text = f"{article['title']} {article.get('summary', '')}"
                sentiment = self._calculate_sentiment(text)
                article['sentiment'] = sentiment
                self.sentiment_scores.append(sentiment)
                
            return bool(self.articles)
            
        except Exception as e:
            st.error(f"Error fetching news: {e}")
            return False

    def _calculate_sentiment(self, text: str) -> Dict[str, float]:
        """
        Calculate sentiment scores for text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with polarity and subjectivity scores
        """
        analysis = TextBlob(text)
        return {
            'polarity': analysis.sentiment.polarity,
            'subjectivity': analysis.sentiment.subjectivity
        }

    def get_sentiment_distribution(self) -> Dict[str, int]:
        """
        Get distribution of sentiment scores
        
        Returns:
            Dict with counts of positive, negative, and neutral articles
        """
        return {
            'positive': sum(1 for s in self.sentiment_scores if s['polarity'] > 0.1),
            'neutral': sum(1 for s in self.sentiment_scores if -0.1 <= s['polarity'] <= 0.1),
            'negative': sum(1 for s in self.sentiment_scores if s['polarity'] < -0.1)
        }

    def create_sentiment_chart(self) -> Optional[go.Figure]:
        """
        Create sentiment trend visualization
        
        Returns:
            Plotly figure or None
        """
        if not self.articles:
            return None
            
        dates = [datetime.fromtimestamp(a['providerPublishTime']) for a in self.articles]
        sentiments = [a['sentiment']['polarity'] for a in self.articles]
        
        fig = go.Figure()
        
        # Add scatter plot with color gradient based on sentiment
        fig.add_trace(go.Scatter(
            x=dates,
            y=sentiments,
            mode='markers+lines',
            name='Sentiment',
            marker=dict(
                size=8,
                color=sentiments,
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title='Sentiment')
            ),
            line=dict(color='rgba(0,0,0,0.2)')
        ))
        
        fig.update_layout(
            title='News Sentiment Trend',
            xaxis_title='Date',
            yaxis_title='Sentiment Score',
            height=400,
            template='plotly_dark',
            showlegend=False
        )
        
        return fig

    def filter_articles(
        self,
        sentiment_filter: str,
        sort_by: str
    ) -> List[Dict]:
        """
        Filter and sort articles based on criteria
        
        Args:
            sentiment_filter: Filter by sentiment category
            sort_by: Sorting criterion
            
        Returns:
            Filtered and sorted list of articles
        """
        # Apply sentiment filter
        if sentiment_filter == "All":
            filtered = self.articles
        else:
            filtered = []
            for article in self.articles:
                polarity = article['sentiment']['polarity']
                if sentiment_filter == "Positive" and polarity > 0.1:
                    filtered.append(article)
                elif sentiment_filter == "Negative" and polarity < -0.1:
                    filtered.append(article)
                elif sentiment_filter == "Neutral" and -0.1 <= polarity <= 0.1:
                    filtered.append(article)
        
        # Sort articles
        if sort_by == "Date (Newest)":
            filtered.sort(key=lambda x: x['providerPublishTime'], reverse=True)
        elif sort_by == "Date (Oldest)":
            filtered.sort(key=lambda x: x['providerPublishTime'])
        elif sort_by == "Sentiment (Highest)":
            filtered.sort(key=lambda x: x['sentiment']['polarity'], reverse=True)
        elif sort_by == "Sentiment (Lowest)":
            filtered.sort(key=lambda x: x['sentiment']['polarity'])
            
        return filtered

def display_news_card(article: Dict):
    """
    Display a single news article card
    
    Args:
        article: News article data
    """
    with st.container():
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {article['title']}")
            st.markdown(f"**Source:** {article.get('publisher', 'Unknown')}")
            st.markdown(
                f"**Date:** {datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M')}"
            )
            st.markdown(article.get('summary', 'No summary available'))
            st.markdown(f"[Read More]({article['link']})")
        
        with col2:
            polarity = article['sentiment']['polarity']
            st.metric(
                "Sentiment",
                f"{polarity:.2f}",
                delta=None,
                delta_color="normal"
            )
            
            if polarity > 0.1:
                st.success("Positive")
            elif polarity < -0.1:
                st.warning("Negative")
            else:
                st.info("Neutral")

def display_news_section(symbol: str, days_back: int = 30):
    """
    Display complete news analysis section
    
    Args:
        symbol: Stock symbol
        days_back: Number of days to look back
    """
    st.header(f"News Analysis - {symbol}")
    
    # Initialize analyzer
    analyzer = NewsAnalyzer(symbol)
    
    # Fetch news
    with st.spinner("Fetching news..."):
        if not analyzer.fetch_news(days_back):
            st.error("Unable to fetch news data")
            return
    
    # News filters and controls
    col1, col2, col3 = st.columns(3)
    with col1:
        sentiment_filter = st.selectbox(
            "Filter by Sentiment",
            ["All", "Positive", "Negative", "Neutral"]
        )
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (Newest)", "Date (Oldest)", 
             "Sentiment (Highest)", "Sentiment (Lowest)"]
        )
    with col3:
        show_sentiment = st.checkbox("Show Sentiment Analysis", True)
    
    # Display sentiment analysis
    if show_sentiment and analyzer.sentiment_scores:
        st.subheader("Sentiment Analysis")
        
        # Distribution metrics
        distribution = analyzer.get_sentiment_distribution()
        cols = st.columns(3)
        with cols[0]:
            st.metric("Positive News", distribution['positive'])
        with cols[1]:
            st.metric("Neutral News", distribution['neutral'])
        with cols[2]:
            st.metric("Negative News", distribution['negative'])
        
        # Sentiment trend chart
        chart = analyzer.create_sentiment_chart()
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    
    # Display filtered articles
    st.subheader("Latest News")
    articles = analyzer.filter_articles(sentiment_filter, sort_by)
    
    if not articles:
        st.info("No news articles found matching the criteria.")
        return
    
    # Display articles with pagination
    articles_per_page = 5
    total_pages = (len(articles) - 1) // articles_per_page + 1
    
    current_page = st.select_slider(
        "Page",
        options=range(1, total_pages + 1),
        value=1
    )
    
    start_idx = (current_page - 1) * articles_per_page
    end_idx = min(start_idx + articles_per_page, len(articles))
    
    for article in articles[start_idx:end_idx]:
        display_news_card(article)

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    symbol = st.text_input("Enter stock symbol:", "AAPL")
    if symbol:
        display_news_section(symbol)