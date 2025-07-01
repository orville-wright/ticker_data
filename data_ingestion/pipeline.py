import logging
import concurrent.futures
from typing import List, Dict

from data_ingestion.alpha_vantage_client import AlphaVantageClient
from data_ingestion.twitter_client import TwitterClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data_for_stock(
    stock_symbol: str,
    alpha_vantage_client: AlphaVantageClient,
    twitter_client: TwitterClient
) -> Dict:
    """
    Fetches price and tweet data for a single stock.

    This helper function is designed to be executed concurrently.

    Args:
        stock_symbol (str): The stock ticker symbol (e.g., "AAPL").
        alpha_vantage_client (AlphaVantageClient): An initialized client for the Alpha Vantage API.
        twitter_client (TwitterClient): An initialized client for the Twitter/X API.

    Returns:
        Dict: A dictionary containing the symbol and the fetched data or an error message.
              Example on success: {"symbol": "AAPL", "data": {"price_data": ..., "tweet_data": ...}, "error": None}
              Example on failure: {"symbol": "AAPL", "data": None, "error": "API fetch failed"}
    """
    logging.info(f"Starting data fetch for: {stock_symbol}")
    try:
        # 1. Fetch Historical Price Data
        price_data = alpha_vantage_client.fetch_daily_time_series(stock_symbol)

        # 2. Fetch Tweet Data
        # The TwitterClient handles the query format, so we just pass the ticker.
        tweet_data = twitter_client.search_tweets(ticker=stock_symbol)

        # 3. Return Success Result
        return {
            "symbol": stock_symbol,
            "data": {
                "price_data": price_data,
                "tweet_data": tweet_data
            },
            "error": None
        }
    except Exception as e:
        # 4. Handle Exceptions
        error_message = f"An unexpected error occurred: {e}"
        logging.error(f"Error fetching data for {stock_symbol}: {error_message}")
        return {
            "symbol": stock_symbol,
            "data": None,
            "error": error_message
        }

def run_ingestion_pipeline(
    stocks: List[str],
    alpha_vantage_client: AlphaVantageClient,
    twitter_client: TwitterClient,
    max_workers: int = 5
) -> Dict:
    """
    Orchestrates the concurrent fetching of data for a list of stock tickers.

    Args:
        stocks (List[str]): A list of stock ticker symbols to process.
        alpha_vantage_client (AlphaVantageClient): An instance of the Alpha Vantage client.
        twitter_client (TwitterClient): An instance of the Twitter client.
        max_workers (int): The maximum number of concurrent threads to use.

    Returns:
        Dict: A dictionary where keys are stock symbols. Each value is another
              dictionary containing 'price_data' and 'tweet_data'. Failed fetches
              will have empty data structures.
    """
    # 1. Initialization
    ingested_data = {}

    # 2. Concurrent Execution using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a future for each stock
        future_to_stock = {
            executor.submit(
                fetch_data_for_stock,
                stock,
                alpha_vantage_client,
                twitter_client
            ): stock for stock in stocks
        }

        logging.info(f"Dispatching {len(stocks)} data fetching tasks to worker pool.")

        # 3. Result Aggregation
        for future in concurrent.futures.as_completed(future_to_stock):
            stock_symbol = future_to_stock[future]
            try:
                result = future.result()
                if result["error"] is None:
                    ingested_data[stock_symbol] = result["data"]
                    logging.info(f"Successfully ingested data for {stock_symbol}")
                else:
                    logging.error(f"Failed to ingest data for {stock_symbol}. Reason: {result['error']}")
                    ingested_data[stock_symbol] = {
                        "price_data": {},
                        "tweet_data": []
                    }
            except Exception as exc:
                logging.error(f'{stock_symbol} generated an exception: {exc}')
                ingested_data[stock_symbol] = {
                    "price_data": {},
                    "tweet_data": []
                }

    logging.info("All data fetching tasks have completed.")
    # 4. Return Result
    return ingested_data