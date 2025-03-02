import pandas as pd
from gnews import GNews
from datetime import datetime, timedelta
import time

class NewsFetcher:
    def __init__(self):
        self.google_news = GNews(language='en', country='IN', period='1d', max_results=1)
        self.last_fetch = {}  # Cache to prevent too frequent requests

    def clean_symbol(self, symbol):
        """Clean the symbol for better news search"""
        return symbol.strip().replace('&', 'and').replace('.', '')

    def get_news_for_symbol(self, symbol):
        try:
            # Rate limiting check
            current_time = time.time()
            if symbol in self.last_fetch and current_time - self.last_fetch[symbol] < 30:
                return None

            clean_symbol = self.clean_symbol(symbol)
            news = self.google_news.get_news(f"{clean_symbol} stock market news")
            self.last_fetch[symbol] = current_time

            if news and len(news) > 0:
                article = news[0]
                return {
                    'title': article['title'],
                    'published_date': article['published date'],
                    'url': article['url']
                }
            return None
        except Exception as e:
            print(f"Error fetching news for {symbol}: {str(e)}")
            return None

    def read_symbols(self, csv_path):
        try:
            # Read CSV with proper encoding and handling
            df = pd.read_csv(csv_path, encoding='utf-8')
            if 'SYMBOL' not in df.columns:
                df = pd.read_csv(csv_path, encoding='utf-8', header=None, names=['SYMBOL'])

            # Clean and filter symbols
            symbols = df['SYMBOL'].dropna().astype(str).tolist()
            return [symbol.strip() for symbol in symbols if symbol.strip()]
        except Exception as e:
            print(f"Error reading CSV: {str(e)}")
            return []