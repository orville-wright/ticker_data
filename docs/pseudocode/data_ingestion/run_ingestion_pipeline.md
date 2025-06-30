# Pseudocode: run_ingestion_pipeline (Concurrent Revision)

This document outlines the revised, language-agnostic pseudocode for the `run_ingestion_pipeline` function, designed for concurrent data fetching to improve performance.

## Function: `fetch_data_for_stock` (Helper)

Fetches price and tweet data for a single stock. This function is designed to be executed concurrently.

### SPARC-compliant Pseudocode

```plaintext
FUNCTION fetch_data_for_stock(stock_symbol, alpha_vantage_client, twitter_client)
  -- Parameters:
  --   stock_symbol (STRING): The stock ticker symbol (e.g., "AAPL").
  --   alpha_vantage_client (OBJECT): An initialized client for the Alpha Vantage API.
  --   twitter_client (OBJECT): An initialized client for the Twitter/X API.
  --
  -- Returns:
  --   (DICTIONARY): A dictionary containing the symbol and the fetched data or an error message.
  --                 Example on success: {"symbol": "AAPL", "data": {"price_data": ..., "tweet_data": ...}, "error": NULL}
  --                 Example on failure: {"symbol": "AAPL", "data": NULL, "error": "API fetch failed"}

  -- TEST: test_fetch_data_for_stock_success
  -- BEHAVIOR: Should return a dictionary with symbol and data on successful API calls.
  -- SETUP: Create mock clients for Alpha Vantage and Twitter.
  -- MOCK: Configure mocks to return valid sample data for "AAPL".
  -- ACTION: Call fetch_data_for_stock("AAPL", mock_av_client, mock_twitter_client).
  -- ASSERT: The returned dictionary's "symbol" key is "AAPL".
  -- ASSERT: The "data" key contains non-empty "price_data" and "tweet_data".
  -- ASSERT: The "error" key is NULL or not present.

  -- TEST: test_fetch_data_for_stock_failure
  -- BEHAVIOR: Should return a dictionary with an error message if an API call fails.
  -- SETUP: Create mock clients.
  -- MOCK: Configure Alpha Vantage mock to raise an exception or return an error.
  -- ACTION: Call fetch_data_for_stock("FAIL", mock_av_client, mock_twitter_client).
  -- ASSERT: The returned dictionary's "symbol" key is "FAIL".
  -- ASSERT: The "data" key is NULL.
  -- ASSERT: The "error" key contains an error message.

  LOG "Starting data fetch for: " + stock_symbol
  TRY
    -- 1. Fetch Historical Price Data
    -- TEST-ANCHOR: Verify alpha_vantage_client.fetch_daily_time_series is called.
    price_data = alpha_vantage_client.fetch_daily_time_series(stock_symbol)

    -- 2. Fetch Tweet Data
    tweet_query = "$" + stock_symbol
    -- TEST-ANCHOR: Verify twitter_client.search_tweets is called.
    tweet_data = twitter_client.search_tweets(tweet_query)

    -- 3. Return Success Result
    RETURN {
      "symbol": stock_symbol,
      "data": {
        "price_data": price_data,
        "tweet_data": tweet_data
      },
      "error": NULL
    }
  CATCH Exception as e
    -- 4. Handle Exceptions
    LOG "Error fetching data for " + stock_symbol + ": " + e.message
    RETURN {
      "symbol": stock_symbol,
      "data": NULL,
      "error": e.message
    }
  ENDTRY
ENDFUNCTION
```

## Function: `run_ingestion_pipeline`

Orchestrates the concurrent fetching of data for a list of stock tickers using a worker pool pattern.

### SPARC-compliant Pseudocode

```plaintext
FUNCTION run_ingestion_pipeline(stocks, alpha_vantage_client, twitter_client)
  -- Parameters:
  --   stocks (LIST of STRING): A list of stock ticker symbols.
  --   alpha_vantage_client (OBJECT): An initialized client for the Alpha Vantage API.
  --   twitter_client (OBJECT): An initialized client for the Twitter/X API.
  --
  -- Returns:
  --   (DICTIONARY): A dictionary where keys are stock symbols and values are dictionaries
  --                 containing 'price_data' and 'tweet_data'. Failed fetches will have empty data.

  -- TEST: test_run_ingestion_pipeline_concurrent_happy_path
  -- BEHAVIOR: Should concurrently fetch and return aggregated data for all stocks.
  -- SETUP: Mock a worker pool and the fetch_data_for_stock helper function.
  -- MOCK: Configure fetch_data_for_stock mock to return successful data structures for ["AAPL", "GOOG"].
  -- ACTION: Call run_ingestion_pipeline with ["AAPL", "GOOG"].
  -- ASSERT: The worker pool was initialized and executed with tasks for "AAPL" and "GOOG".
  -- ASSERT: The final dictionary contains "AAPL" and "GOOG" keys with their respective data.

  -- TEST: test_run_ingestion_pipeline_with_partial_failures
  -- BEHAVIOR: Should successfully aggregate data for successful tasks even if others fail.
  -- SETUP: Mock a worker pool and the fetch_data_for_stock helper function.
  -- MOCK: Configure fetch_data_for_stock to return success for "AAPL" and an error for "FAIL".
  -- ACTION: Call run_ingestion_pipeline with ["AAPL", "FAIL"].
  -- ASSERT: The final dictionary contains "AAPL" with valid data.
  -- ASSERT: The final dictionary contains "FAIL" with empty data structures.

  -- 1. Initialization
  INITIALIZE an empty DICTIONARY named `ingested_data`.
  INITIALIZE an empty LIST named `tasks_to_run`.
  INITIALIZE a concurrent worker pool (e.g., a ThreadPool or an asyncio TaskGroup).

  -- 2. Task Creation
  -- Create a task for each stock symbol to be executed by the helper function.
  FOR EACH stock_symbol IN stocks
    CREATE a task to call `fetch_data_for_stock(stock_symbol, alpha_vantage_client, twitter_client)`.
    ADD the task to `tasks_to_run`.
  ENDFOR

  -- 3. Concurrent Execution
  -- Dispatch all tasks to the worker pool and wait for all of them to complete.
  LOG "Dispatching " + length(tasks_to_run) + " data fetching tasks to worker pool."
  completed_results = worker_pool.execute_and_wait_for_all(tasks_to_run)
  LOG "All data fetching tasks have completed."

  -- 4. Result Aggregation
  -- Process the results from each completed task.
  FOR EACH result IN completed_results
    stock_symbol = result["symbol"]
    IF result["error"] IS NULL THEN
      -- Store successfully fetched data.
      ingested_data[stock_symbol] = result["data"]
      LOG "Successfully ingested data for " + stock_symbol
    ELSE
      -- Handle failed tasks by storing empty data and logging the error.
      LOG "Failed to ingest data for " + stock_symbol + ". Reason: " + result["error"]
      ingested_data[stock_symbol] = {
        "price_data": {}, -- Empty dictionary
        "tweet_data": []  -- Empty list
      }
    ENDIF
  ENDFOR

  -- 5. Return Result
  RETURN ingested_data

ENDFUNCTION
```

### Dependencies

-   [`alpha_vantage_client.fetch_daily_time_series`](docs/pseudocode/data_ingestion/fetch_daily_time_series.md)
-   [`twitter_client.search_tweets`](docs/pseudocode/data_ingestion/twitter_client_search_tweets.md)

### TDD Anchors Summary

1.  **`test_fetch_data_for_stock_success`**: Verifies the helper function correctly fetches and returns data for a single stock.
2.  **`test_fetch_data_for_stock_failure`**: Ensures the helper function gracefully handles API errors and returns a structured error message.
3.  **`test_run_ingestion_pipeline_concurrent_happy_path`**: Verifies the main pipeline correctly orchestrates concurrent tasks and aggregates the results.
4.  **`test_run_ingestion_pipeline_with_partial_failures`**: Ensures the pipeline is resilient, continuing to process results from successful tasks even when others fail concurrently.