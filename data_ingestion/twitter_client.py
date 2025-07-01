import logging
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TwitterClient:
    """
    A client to interact with the Twitter/X API v2 using a persistent, resilient session.
    """
    BASE_URL = "https://api.twitter.com/2/tweets/search/recent"
    DEFAULT_TWEET_FIELDS = "created_at,public_metrics,lang"
    QUERY_TEMPLATE = "#{ticker} lang:en -is:retweet"

    def __init__(self, bearer_token: str, max_retries: int = 3, backoff_factor: float = 1.0):
        """
        Initializes the client with a bearer token and a resilient requests session.

        The session is configured with an HTTPAdapter that automatically handles
        retries for specific HTTP status codes and connection errors using an
        exponential backoff strategy.

        Args:
            bearer_token (str): The Twitter API v2 bearer token.
            max_retries (int): The maximum number of retry attempts.
            backoff_factor (float): The backoff factor for calculating retry delay.
                                  (e.g., {backoff factor} * (2 ** ({number of total retries} - 1)))
        """
        if not isinstance(bearer_token, str) or not bearer_token:
            raise ValueError("Bearer token cannot be null or empty.")

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {bearer_token}"})

        # Configure a robust retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry on
            backoff_factor=backoff_factor,
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        # Mount the retry strategy to the session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)


    def search_tweets(self, ticker: str, max_tweets: int = 100) -> list[dict]:
        """
        Searches for recent tweets mentioning a specific stock ticker, handling pagination.

        Args:
            ticker (str): The stock ticker symbol (e.g., "AAPL").
            max_tweets (int): The maximum number of tweets to return.

        Returns:
            list[dict]: A list of tweet objects, or an empty list if the request fails.
        """
        if not re.match(r"^[a-zA-Z0-9]{1,6}$", ticker):
            raise ValueError("Invalid ticker format. Ticker must be 1-6 alphanumeric characters.")

        all_tweets = []
        query = self.QUERY_TEMPLATE.format(ticker=ticker)
        params = {
            'query': query,
            'tweet.fields': self.DEFAULT_TWEET_FIELDS,
            'max_results': min(max_tweets, 100)
        }

        while True:
            try:
                logging.debug(f"Searching tweets with params: {params}")
                response = self.session.get(self.BASE_URL, params=params, timeout=10)
                response.raise_for_status()

                response_data = response.json()
                data = response_data.get("data", [])
                meta = response_data.get("meta", {})
                
                if not data:
                    logging.info(f"No more tweets found for ticker {ticker}.")
                    break
                
                logging.info(f"Successfully fetched {len(data)} tweets for ticker {ticker}.")
                all_tweets.extend(data)
                
                next_token = meta.get("next_token")
                
                if len(all_tweets) >= max_tweets or not next_token:
                    break
                
                logging.info(f"Paginating... fetching next page for ticker {ticker} with token {next_token}.")
                params['pagination_token'] = next_token
                params['max_results'] = min(max_tweets - len(all_tweets), 100)

            except requests.exceptions.HTTPError as e:
                try:
                    error_payload = e.response.json()
                    error_title = error_payload.get("title", "N/A")
                    error_detail = error_payload.get("detail", "No detail provided.")
                    logging.error(
                        f"HTTP error {e.response.status_code} for ticker {ticker} after retries. "
                        f"Title: {error_title}, Detail: {error_detail}"
                    )
                except requests.exceptions.JSONDecodeError:
                    logging.error(
                        f"Unrecoverable HTTP error {e.response.status_code} for ticker {ticker} after retries: {e.response.text}"
                    )
                return []
            
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to fetch tweets for ticker {ticker} after retries. Error: {e}")
                return []

        final_tweets = all_tweets[:max_tweets]
        logging.info(f"Successfully fetched {len(final_tweets)} tweets for ticker {ticker}.")
        return final_tweets