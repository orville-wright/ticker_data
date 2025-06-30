# Specification: Data Ingestion

This document details the technical specifications for the data ingestion components of the AI-powered stock trend prediction platform. These components are responsible for fetching raw data from external sources.

## 1. Overview

The data ingestion module will consist of two primary components:
- A client for fetching historical stock data from Alpha Vantage.
- A client for fetching social media data from the Twitter/X API.

These components must be robust, handle API errors and rate limits gracefully, and provide a consistent output format for the data processing module.

---

## 2. Alpha Vantage Client

This component will fetch historical time-series data for specified stock tickers.

### 2.1. Class: `AlphaVantageClient`

A client to interact with the Alpha Vantage API.

#### Properties

-   `api_key` (str): The API key for authenticating with Alpha Vantage.
-   `base_url` (str): The base URL for the Alpha Vantage API (e.g., "https://www.alphavantage.co/query").

#### Methods

-   `__init__(self, api_key: str)`
    -   **Description:** Initializes the client with the provided API key.
    -   **Parameters:**
        -   `api_key` (str): The Alpha Vantage API key.
    -   **Returns:** `None`

-   `fetch_daily_time_series(self, symbol: str, output_size: str = 'compact') -> dict`
    -   **Description:** Fetches the daily time-series data (open, high, low, close, volume) for a given stock symbol.
    -   **Parameters:**
        -   `symbol` (str): The stock ticker symbol (e.g., "AAPL").
        -   `output_size` (str): The size of the output data. 'compact' returns the latest 100 data points; 'full' returns the full-length time series. Defaults to 'compact'.
    -   **Returns:** `dict`: A dictionary containing the time-series data, or an empty dictionary if the request fails.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_fetch_daily_time_series_success
        # BEHAVIOR: Should return a dictionary with time-series data for a valid symbol.
        # MOCK: mock requests.get to return a sample Alpha Vantage JSON response.
        # ASSERT: The returned dictionary contains the expected keys ('Time Series (Daily)').

        # TEST: test_fetch_daily_time_series_api_error
        # BEHAVIOR: Should handle API errors gracefully.
        # MOCK: mock requests.get to raise an exception or return an error status code.
        # ASSERT: The method returns an empty dictionary and logs an error message.
 
        # TEST: test_fetch_daily_time_series_rate_limit_with_backoff
        # BEHAVIOR: Should handle 429 errors by retrying with exponential backoff.
        # MOCK: mock requests.get to return a 429 status code on the first call, then a 200 on the second.
        # SETUP: import time, mock time.sleep
        # PSEUDOCODE:
        #   attempts = 0
        #   delay = 1
        #   while attempts < MAX_RETRIES:
        #     response = requests.get(...)
        #     if response.status_code == 429:
        #       time.sleep(delay)
        #       delay *= 2 # Exponential backoff
        #       attempts += 1
        #     elif response.status_code == 200:
        #       return response.json()
        #     else:
        #       return {} # Or raise exception
        #   # Log failure after max retries
        #   return {}
        # ASSERT: time.sleep is called with increasing delays.
        # ASSERT: The method eventually returns the successful response data.
        ```

---

## 3. Twitter/X API Client

This component will fetch tweets mentioning specific stock tickers.

### 3.1. Class: `TwitterClient`

A client to interact with the Twitter/X API v2.

#### Properties

-   `bearer_token` (str): The bearer token for authenticating with the Twitter/X API.
-   `base_url` (str): The base URL for the Twitter API (e.g., "https://api.twitter.com/2/tweets/search/recent").

#### Methods

-   `__init__(self, bearer_token: str)`
    -   **Description:** Initializes the client with the provided bearer token.
    -   **Parameters:**
        -   `bearer_token` (str): The Twitter API v2 bearer token.
    -   **Returns:** `None`

-   `search_tweets(self, query: str, max_results: int = 100) -> list[dict]`
    -   **Description:** Searches for recent tweets matching a specific query (e.g., "$AAPL").
    -   **Parameters:**
        -   `query` (str): The search query. Should include the stock ticker with a cashtag (e.g., "$MSFT").
        -   `max_results` (int): The maximum number of tweets to return (min 10, max 100). Defaults to 100.
    -   **Returns:** `list[dict]`: A list of tweet objects, where each object is a dictionary. Returns an empty list if the request fails.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_search_tweets_success
        # BEHAVIOR: Should return a list of tweet dictionaries for a valid query.
        # MOCK: mock requests.get to return a sample Twitter API JSON response.
        # ASSERT: The returned list is not empty and its elements are dictionaries with 'id' and 'text' keys.

        # TEST: test_search_tweets_rate_limit_with_backoff
        # BEHAVIOR: Should handle 429 errors by retrying with exponential backoff.
        # MOCK: mock requests.get to return a 429 status code on the first call, then a 200 on the second.
        # SETUP: import time, mock time.sleep
        # PSEUDOCODE:
        #   attempts = 0
        #   delay = 1
        #   while attempts < MAX_RETRIES:
        #     response = requests.get(...)
        #     if response.status_code == 429:
        #       time.sleep(delay)
        #       delay *= 2 # Exponential backoff
        #       attempts += 1
        #     elif response.status_code == 200:
        #       return response.json()['data']
        #     else:
        #       return [] # Or raise exception
        #   # Log failure after max retries
        #   return []
        # ASSERT: time.sleep is called with increasing delays.
        # ASSERT: The method eventually returns the successful list of tweets.
        ```

---

## 4. Data Ingestion Orchestrator

This function will orchestrate the data fetching process for a list of stocks.

### 4.1. Function: `run_ingestion_pipeline(stocks: list[str], alpha_vantage_client: AlphaVantageClient, twitter_client: TwitterClient) -> dict`

Orchestrates the fetching of data for a list of stock tickers.

-   **Description:** For each stock in the list, this function calls the appropriate methods from the `AlphaVantageClient` and `TwitterClient` to fetch both historical price data and recent tweets. The data is then stored in a structured format.
-   **Parameters:**
    -   `stocks` (list[str]): A list of stock ticker symbols to process.
    -   `alpha_vantage_client` (AlphaVantageClient): An instance of the Alpha Vantage client.
    -   `twitter_client` (TwitterClient): An instance of the Twitter client.
-   **Returns:** `dict`: A dictionary where keys are stock symbols. Each value is another dictionary containing 'price_data' and 'tweet_data'.
-   **TDD Anchor/Pseudocode Stub:**
    ```python
    # TEST: test_run_ingestion_pipeline
    # BEHAVIOR: Should return a dictionary containing fetched data for all specified stocks.
    # SETUP: Create mock instances of AlphaVantageClient and TwitterClient.
    # MOCK: Configure the mock clients to return sample data for specific symbols.
    # ACTION: Call run_ingestion_pipeline with a list of symbols.
    # ASSERT: The returned dictionary has keys for each symbol and contains the expected 'price_data' and 'tweet_data'.