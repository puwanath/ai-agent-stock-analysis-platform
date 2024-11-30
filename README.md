# AI-Agents Stock Analyst Platform

AI-powered stock analysis platform supporting both Thai (SET) and International stocks with comprehensive technical, fundamental, and AI-driven analysis.

![Platform Preview](https://github.com/puwanath/ai-agent-stock-analysis-platform/blob/main/capture_screen/Screen%20(12).png?raw=true)

## 🌟 Features

### Stock Analysis
- Real-time stock data for Thai (SET) and International markets
- Advanced technical analysis with multiple indicators
- Fundamental analysis with financial metrics
- AI-powered stock recommendations using local LLMs
- News sentiment analysis

### Technical Analysis
- Moving Averages (SMA, EMA)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume Analysis
- Support and Resistance Levels

### Financial Analysis
- Key financial ratios
- Profitability metrics
- Growth analysis
- Valuation metrics
- Financial health indicators

### AI Analysis
- AI-powered buy/sell/hold recommendations
- Confidence level assessment
- Risk analysis
- Price target predictions
- Thai language support
- Powered by Ollama (Local LLM)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Ollama (for AI analysis)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/puwanath/stock-analysis-platform.git
cd stock-analysis-platform
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Install and start Ollama (for AI analysis):
```bash
# Follow instructions at https://ollama.ai/
# Pull the Mistral model
ollama pull llama3.1:latest
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to:
```
http://localhost:8501
```

## 📁 Project Structure

```
ai_agents_stock_analysis_platform/
├── app.py                    # Main application file
├── requirements.txt          # Project dependencies
├── utils/
│   ├── __init__.py
    ├── calculations.py        # Common calculations
│   ├── data_fetcher.py      # Data fetching utilities
|   ├── formatters.py       # Data formatting utilities
│   ├── technical_indicators.py  # Technical analysis
│   ├── financial_metrics.py    # Financial calculations
│   └── thai_stock_fetcher.py   # Thai stock utilities
├── components/
│   ├── __init__.py
│   ├── company_info.py      # Company information display
│   ├── technical.py         # Technical analysis display
│   ├── financial.py         # Financial information display
│   ├── news.py             # News section display
│   ├── risk.py             # Risk metrics display
│   ├── charts.py           # Chart creation utilities
│   ├── research.py         # Research section display
│   └── ai_analyzer.py      # AI analysis component
└── config/
    ├── __init__.py
    └── settings.py          # Application settings
```

## ⚙️ Configuration

You can configure the application through `config/settings.py`:

```python
# AI Analysis Settings
AI_CONFIG = {
    'ai_analysis': {
        'enabled': True,  # Enable/disable AI analysis
        'api_url': 'http://localhost:11434/api/generate',
        'model': 'llama3.1:latest',
        'timeout': 60
    }
}
```

## 🔧 Usage

1. Enter a stock symbol (e.g., AAPL, PTT.BK)
2. Select time period and analysis type
3. Enable/disable AI analysis as needed
4. Click "Analyze" to start analysis

## 🤖 AI Analysis

The platform uses Ollama for AI-powered analysis. Ensure Ollama is running and the Mistral model is installed:

```bash
# Check Ollama status
curl http://localhost:11434/api/generate

# Pull Mistral model if not installed
ollama pull llama3.1:latest
```

## 📊 Data Sources

- International Stocks: Yahoo Finance
- Thai Stocks: SET Market + Yahoo Finance
- News: Various financial news sources
- Company Information: Stock exchange data

## 🛡️ Disclaimer

This platform is for informational purposes only. Always conduct your own research and consult with a financial advisor before making investment decisions.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## ✨ Credits

- Data powered by Yahoo Finance and SET Market
- AI analysis powered by [Ollama](https://ollama.ai/)
- Built with [Streamlit](https://streamlit.io/)
- Cody AI for code Debugging & Reviewing
- Claude AI for Researching & Writing README.md
- Yahoo Finance for stock data

## Developer Team
- [Puwanath Baibua](https://github.com/puwanath)

## 📧 Support

For support and questions, please open an issue in the GitHub repository.
