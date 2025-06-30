import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AlphaVantageClient:
    """
    A client to interact with the Alpha Vantage API for fetching stock data.
    """
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str, max_retries: int = 3):
        """
        Initializes the AlphaVantageClient.

        Args:
            api_key (str): The API key for Alpha Vantage.
            max_retries (int): The maximum number of retries for an API call.
        
        Raises:
            ValueError: If the api_key is not a non-empty string.
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string.")
        
        self.api_key = api_key
        self.max_retries = max_retries

    def fetch_daily_time_series(self, symbol: str, output_size: str = 'compact') -> dict:
        """
        Fetches the daily time-series data for a given stock symbol.

        Implements an exponential backoff retry mechanism for handling rate limits
        and transient API errors.

        Args:
            symbol (str): The stock ticker symbol (e.g., "AAPL").
            output_size (str): The size of the output data. 'compact' returns the
                               latest 100 data points; 'full' returns the full-length
                               time series. Defaults to 'compact'.

        Returns:
            dict: A dictionary containing the time-series data, or an empty
                  dictionary if the request fails after all retries.
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': output_size,
            'apikey': self.api_key
        }
        
        attempts = 0
        delay = 1  # Initial delay in seconds

        while attempts < self.max_retries:
            try:
                response = requests.get(self.BASE_URL, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if "Error Message" in data:
                        logging.error(f"API returned an error for symbol {symbol}: {data['Error Message']}")
                        return {} # Permanent error for this symbol, no retry
                    if "Note" in data and "call frequency" in data["Note"]:
                        logging.warning(f"Rate limit warning received for symbol {symbol}. Retrying...")
                        # This will fall through to the backoff logic
                    else:
                        logging.info(f"Successfully fetched data for symbol: {symbol}")
                        return data

                elif response.status_code == 429:
                    logging.warning(f"Rate limit hit (429) for symbol {symbol}. Retrying in {delay} seconds...")

                else:
                    logging.error(f"HTTP error for symbol {symbol}: {response.status_code} {response.reason}")
                    # This is likely a non-transient error, so we return immediately.
                    return {}
            
            except requests.exceptions.RequestException as e:
                logging.error(f"Network error for symbol {symbol} on attempt {attempts + 1}: {e}")

            time.sleep(delay)
            delay *= 2  # Exponential backoff
            attempts += 1
            
        logging.error(f"Failed to fetch data for symbol: {symbol} after {self.max_retries} attempts.")
        return {}