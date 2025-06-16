# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based financial data extraction and analysis toolkit that scrapes real-time stock data from multiple sources (Yahoo Finance, NASDAQ, MarketWatch, BigCharts, Alpaca) and performs ML/NLP sentiment analysis on financial news articles.

## Development Environment

**Python Environment:**
- Requires Python 3.12+
- Uses virtual environment at `/home/dbrace/venv/dave02/`
- Always activate the virtual environment before running code:
```bash
source /home/dbrace/venv/dave02/bin/activate
```

**Dependencies:**
Install all required packages:
```bash
pip install -r requirements.txt
```

## Architecture

### Module Naming Convention
- `y_*.py` - Yahoo Finance data extractors
- `nasdaq_*.py` - NASDAQ.com data extractors  
- `ml_*.py` - Machine learning and NLP modules
- `*_md.py` - Market data extractors for other sources

### Data Pipeline Architecture
1. **Web Scrapers**: Extract live data using BeautifulSoup4 and requests_html
2. **API Integrations**: Native APIs for NASDAQ and Alpaca
3. **Data Processing**: Convert to Pandas DataFrames, NumPy arrays, Python dicts
4. **ML/NLP Pipeline**: Sentiment analysis using scikit-learn, NLTK, transformers
5. **Graph Database**: Neo4j integration for relationship mapping

### Key Data Sources
- **Yahoo Finance**: Top gainers/losers, small caps, tech events, news feeds
- **NASDAQ**: Real-time quotes, unusual volume detection
- **MarketWatch/BigCharts**: Live quotes, company details
- **Alpaca**: Live quotes, 60-second OHLCV candlestick data

### ML/NLP Components
- **ml_sentiment.py**: Core sentiment analysis engine
- **ml_cvbow.py**: Count vectorizer and bag-of-words processing
- **ml_nlpreader.py**: Natural language processing pipeline
- **ml_urlhinter.py**: URL classification and credibility scoring
- **ml_yahoofinews.py**: Yahoo Finance news processing

## Running Individual Modules

Execute modules directly:
```bash
python nasdaq_quotes.py
python y_topgainers.py
python ml_sentiment.py
```

## Important Notes

- **Data Schema Volatility**: Financial websites frequently update their data schemas, breaking scrapers
- **Rate Limiting**: Web scrapers may encounter rate limits or anti-bot measures
- **API Keys**: Alpaca integration requires API credentials
- **Real-time Data**: Most extractors work with live market data during trading hours
- **Cookie Management**: Yahoo Finance modules use `y_cookiemonster.py` for session management

## Recent Updates
- Add neo4j backend server to the stock pricing system