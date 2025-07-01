import re
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pytz
from pandas.tseries.holiday import USFederalHolidayCalendar
from datetime import timedelta

class TweetProcessor:
    """
    A utility class for cleaning and tokenizing tweet text.
    """
    @staticmethod
    def clean_tweet(text: str) -> str:
        """
        A static method that takes raw tweet text and performs cleaning operations.
        It removes URLs, user mentions (@), hashtag symbols (#), special characters,
        and converts the text to lowercase. It retains the '$' for cashtags.
        """
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove user mentions
        text = re.sub(r'@\w+', '', text)
        # Remove hashtag symbols but keep the text
        text = re.sub(r'#', '', text)
        # Convert to lowercase and strip extra whitespace
        return " ".join(text.lower().split())

    @staticmethod
    def tokenize_and_remove_stopwords(text: str, stopwords: set) -> list[str]:
        """
        A static method that tokenizes the cleaned text and removes common English stop words.
        """
        if not text:
            return []
        tokens = word_tokenize(text)
        return [word for word in tokens if word not in stopwords]

class FeatureEngineer:
    """
    A utility class for calculating financial technical indicators.
    """
    @staticmethod
    def calculate_moving_average(data: pd.DataFrame, window: int) -> pd.Series:
        """
        Calculates the Simple Moving Average (SMA) for the 'close' price.
        """
        return data['close'].rolling(window=window).mean()

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calculates the Relative Strength Index (RSI).
        """
        delta = data['close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9) -> tuple[pd.Series, pd.Series]:
        """
        Calculates the Moving Average Convergence Divergence (MACD) and its signal line.
        """
        fast_ema = data['close'].ewm(span=fast_window, adjust=False).mean()
        slow_ema = data['close'].ewm(span=slow_window, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
        return macd_line, signal_line

    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20) -> tuple[pd.Series, pd.Series]:
        """
        Calculates the upper and lower Bollinger Bands.
        """
        sma = data['close'].rolling(window=window).mean()
        std = data['close'].rolling(window=window).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band, lower_band

    @staticmethod
    def add_all_features(data: pd.DataFrame) -> pd.DataFrame:
        """
        Applies all feature engineering functions to the price data DataFrame
        and returns it with the new feature columns.
        """
        data['SMA_20'] = FeatureEngineer.calculate_moving_average(data, window=20)
        data['RSI_14'] = FeatureEngineer.calculate_rsi(data, window=14)
        data['MACD'], data['MACD_Signal'] = FeatureEngineer.calculate_macd(data)
        data['Upper_Bollinger'], data['Lower_Bollinger'] = FeatureEngineer.calculate_bollinger_bands(data, window=20)
        return data.dropna()


def run_processing_pipeline(raw_data: dict, sentiment_model: 'SentimentAnalysisModel') -> dict:
    """
    Orchestrates the entire data processing pipeline.
    
    Args:
        raw_data (dict): The dictionary output from run_ingestion_pipeline.
        sentiment_model (SentimentAnalysisModel): An instantiated sentiment analysis model.

    Returns:
        dict: A dictionary of feature-rich DataFrames for each stock.
    """
    processed_data = {}
    stop_words = set(stopwords.words('english'))
    
    market_timezone = pytz.timezone('America/New_York')
    holidays = USFederalHolidayCalendar().holidays(start='2020-01-01', end='2025-12-31').date

    for stock_symbol, data in raw_data.items():
        price_data_df = data.get('price_data')
        tweet_data_df = data.get('tweet_data')

        if price_data_df is None or price_data_df.empty:
            continue

        # Feature Engineering
        features_df = FeatureEngineer.add_all_features(price_data_df.copy())
        features_df.index = pd.to_datetime(features_df.index)

        daily_sentiment_df = pd.DataFrame(index=features_df.index, columns=['daily_sentiment_score'])
        daily_sentiment_df['daily_sentiment_score'] = 0.0

        if tweet_data_df is not None and not tweet_data_df.empty:
            # Tweet Processing and Sentiment Analysis
            tweet_data_df['cleaned_text'] = tweet_data_df['text'].apply(TweetProcessor.clean_tweet)
            tweet_data_df['tokens'] = tweet_data_df['cleaned_text'].apply(
                lambda x: TweetProcessor.tokenize_and_remove_stopwords(x, stop_words)
            )
            tweet_data_df['sentiment_score'] = sentiment_model.predict(tweet_data_df['tokens'])
            
            # Temporal Alignment
            tweet_data_df['timestamp_tz'] = pd.to_datetime(tweet_data_df['created_at']).dt.tz_localize('UTC').dt.tz_convert(market_timezone)
            
            def get_trading_day(timestamp):
                # If after 4 PM, it's for the next day
                if timestamp.hour >= 16:
                    trading_day = timestamp.date() + timedelta(days=1)
                else:
                    trading_day = timestamp.date()
                
                # Roll forward if it's a weekend or holiday
                while trading_day.weekday() >= 5 or trading_day in holidays:
                    trading_day += timedelta(days=1)
                return trading_day

            tweet_data_df['trading_day'] = tweet_data_df['timestamp_tz'].apply(get_trading_day)
            
            # Aggregate sentiment
            aggregated_sentiment = tweet_data_df.groupby('trading_day')['sentiment_score'].mean()
            aggregated_sentiment.index = pd.to_datetime(aggregated_sentiment.index)
            
            # Update the daily sentiment df
            daily_sentiment_df.update(aggregated_sentiment.rename('daily_sentiment_score'))


        # Merge sentiment scores
        final_df = features_df.join(daily_sentiment_df)
        final_df['daily_sentiment_score'] = final_df['daily_sentiment_score'].fillna(0.0)

        processed_data[stock_symbol] = final_df

    return processed_data