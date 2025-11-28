"""
Data Fetching Utility for ARION
Fetches market data from Yahoo Finance and news sentiment
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class DataFetcher:
    """Fetches and processes market data for ARION agents"""
    
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        
    def fetch_stock_data(self, symbols: List[str], period: str = '3mo', interval: str = '1d') -> Dict[str, pd.DataFrame]:
        """
        Fetch historical stock data for given symbols
        
        Args:
            symbols: List of stock symbols
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            Dictionary mapping symbols to DataFrames with OHLCV data
        """
        data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)
                
                if not df.empty:
                    # Calculate additional metrics
                    df['Returns'] = df['Close'].pct_change()
                    df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
                    df['SMA_20'] = df['Close'].rolling(window=20).mean()
                    df['SMA_50'] = df['Close'].rolling(window=50).mean()
                    
                    # Calculate drawdown
                    cumulative = (1 + df['Returns']).cumprod()
                    running_max = cumulative.expanding().max()
                    df['Drawdown'] = (cumulative - running_max) / running_max
                    
                    data[symbol] = df
                else:
                    print(f"Warning: No data retrieved for {symbol}")
                    
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")
                
        return data
    
    def fetch_current_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch current price and basic info for symbols
        
        Returns:
            Dictionary with current price, change, volume, etc.
        """
        current_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_data[symbol] = {
                    'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                    'change': info.get('regularMarketChange', 0),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('volume', 0),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown')
                }
            except Exception as e:
                print(f"Error fetching current data for {symbol}: {str(e)}")
                current_data[symbol] = {
                    'price': 0,
                    'change': 0,
                    'change_percent': 0,
                    'volume': 0,
                    'market_cap': 0,
                    'pe_ratio': 0,
                    'sector': 'Unknown',
                    'industry': 'Unknown'
                }
                
        return current_data
    
    def fetch_news(self, symbols: List[str], days: int = 7) -> Dict[str, List[Dict]]:
        """
        Fetch recent news headlines for symbols
        
        Args:
            symbols: List of stock symbols
            days: Number of days to look back
            
        Returns:
            Dictionary mapping symbols to list of news articles
        """
        news_data = {}
        
        if not self.news_api_key:
            # Fallback: Use yfinance news
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    news = ticker.news[:10] if hasattr(ticker, 'news') else []
                    
                    news_data[symbol] = [
                        {
                            'title': article.get('title', ''),
                            'publisher': article.get('publisher', ''),
                            'link': article.get('link', ''),
                            'published': article.get('providerPublishTime', 0)
                        }
                        for article in news
                    ]
                except Exception as e:
                    print(f"Error fetching news for {symbol}: {str(e)}")
                    news_data[symbol] = []
        else:
            # Use News API if key is available
            for symbol in symbols:
                try:
                    url = f"https://newsapi.org/v2/everything"
                    params = {
                        'q': symbol,
                        'apiKey': self.news_api_key,
                        'language': 'en',
                        'sortBy': 'publishedAt',
                        'pageSize': 10,
                        'from': (datetime.now() - timedelta(days=days)).isoformat()
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        articles = response.json().get('articles', [])
                        news_data[symbol] = [
                            {
                                'title': article.get('title', ''),
                                'publisher': article.get('source', {}).get('name', ''),
                                'link': article.get('url', ''),
                                'published': article.get('publishedAt', '')
                            }
                            for article in articles
                        ]
                    else:
                        news_data[symbol] = []
                        
                except Exception as e:
                    print(f"Error fetching news for {symbol}: {str(e)}")
                    news_data[symbol] = []
                    
        return news_data
    
    def calculate_portfolio_metrics(self, data: Dict[str, pd.DataFrame], weights: Optional[Dict[str, float]] = None) -> Dict:
        """
        Calculate portfolio-level metrics
        
        Args:
            data: Dictionary of stock DataFrames
            weights: Optional portfolio weights (defaults to equal weight)
            
        Returns:
            Dictionary of portfolio metrics
        """
        if not data:
            return {}
        
        # Default to equal weights
        if weights is None:
            n = len(data)
            weights = {symbol: 1/n for symbol in data.keys()}
        
        # Align all dataframes to same dates
        returns_df = pd.DataFrame({
            symbol: df['Returns'] for symbol, df in data.items()
        }).dropna()
        
        if returns_df.empty:
            return {}
        
        # Calculate weighted portfolio returns
        portfolio_returns = sum(returns_df[symbol] * weights.get(symbol, 0) for symbol in returns_df.columns)
        
        # Portfolio metrics
        metrics = {
            'total_return': (1 + portfolio_returns).prod() - 1,
            'annualized_return': portfolio_returns.mean() * 252,
            'volatility': portfolio_returns.std() * np.sqrt(252),
            'sharpe_ratio': (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252) if portfolio_returns.std() > 0 else 0,
            'max_drawdown': ((1 + portfolio_returns).cumprod() / (1 + portfolio_returns).cumprod().expanding().max() - 1).min(),
            'current_drawdown': ((1 + portfolio_returns).cumprod().iloc[-1] / (1 + portfolio_returns).cumprod().max() - 1)
        }
        
        return metrics


if __name__ == "__main__":
    # Test the data fetcher
    fetcher = DataFetcher()
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    print("Fetching stock data...")
    data = fetcher.fetch_stock_data(symbols, period='1mo')
    
    for symbol, df in data.items():
        print(f"\n{symbol}:")
        print(df.tail())
    
    print("\nFetching current prices...")
    current = fetcher.fetch_current_prices(symbols)
    print(current)
    
    print("\nCalculating portfolio metrics...")
    metrics = fetcher.calculate_portfolio_metrics(data)
    print(metrics)
