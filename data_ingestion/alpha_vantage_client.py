import requests
import time
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AlphaVantageClient:
    """
    A client to interact with the Alpha Vantage API for fetching stock data.
    """

    def __init__(self, api_key: str, max_retries: int = 3, timeout: int = 30):
        """
        Initializes the AlphaVantageClient.

        Args:
            api_key (str): The API key for Alpha Vantage.
            max_retries (int): The maximum number of retries for an API call.
            timeout (int): The request timeout in seconds.
        
        Raises:
            ValueError: If the api_key is not a non-empty string.
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string.")
        
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Use a session object for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TickerData/1.0'})

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
        if not re.match(r'^[A-Z0-9.]{1,10}$', symbol):
            logging.error(f"Invalid symbol format provided: {symbol}")
            return {}

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
                response = self.session.get(self.base_url, params=params, timeout=self.timeout)

                if response.status_code == 200:
                    data = response.json()
                    if "Error Message" in data:
                        logging.error(f"API returned an error for symbol {symbol}: {data['Error Message']}")
                        return {}
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
                    return {}
            
            except requests.exceptions.RequestException as e:
                logging.error(f"Network error for symbol {symbol} on attempt {attempts + 1}: {e}")

            time.sleep(delay)
            delay *= 2  # Exponential backoff
            attempts += 1
            
        logging.error(f"Failed to fetch data for symbol: {symbol} after {self.max_retries} attempts.")
        return {}