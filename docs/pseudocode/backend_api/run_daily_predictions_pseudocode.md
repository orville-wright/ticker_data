# Pseudocode: `run_daily_predictions`

This document outlines the detailed, language-agnostic pseudocode for the `run_daily_predictions` function. This function is designed to be a daily scheduled job that executes the end-to-end pipeline for generating new stock predictions.

## 1. Function Definition

```
FUNCTION run_daily_predictions()
```

### 1.1. Description

A daily scheduled job that runs the entire data ingestion, processing, and prediction pipeline for all relevant stocks. It orchestrates getting the necessary data, processing it, generating predictions with trained models, and storing the results.

### 1.2. Parameters

-   None

### 1.3. Returns

-   None

### 1.4. TDD Anchors

-   **TEST:** `test_run_daily_predictions_success_path`
    -   **BEHAVIOR:** Should successfully execute the full pipeline for a set of tracked stocks, resulting in new predictions being stored in the database and cache.
    -   **SETUP:**
        -   Mock the database to return a list of unique stock symbols (e.g., 'AAPL', 'GOOG').
        -   Mock the `run_ingestion_pipeline`, `run_processing_pipeline`, `PredictionModel.load_model`, `model.predict`, `database.store_prediction`, and `PredictionCache.set` functions to track their calls and return expected values.
    -   **ACTION:** Call `run_daily_predictions()`.
    -   **ASSERT:**
        -   Verify that `run_ingestion_pipeline` and `run_processing_pipeline` were called with the correct list of stocks.
        -   Verify that for each stock, the `load_model`, `predict`, `store_prediction`, and `set` cache methods were called.
        -   Verify that the process completes without errors.

-   **TEST:** `test_run_daily_predictions_no_tracked_stocks`
    -   **BEHAVIOR:** The function should log a message and exit gracefully if no stocks are found in any user watchlists.
    -   **SETUP:** Mock the database to return an empty list of stocks.
    -   **ACTION:** Call `run_daily_predictions()`.
    -   **ASSERT:**
        -   Verify that a log message indicating no stocks to process is generated.
        -   Verify that the ingestion, processing, and prediction loops are not executed.

-   **TEST:** `test_run_daily_predictions_model_not_found_for_one_stock`
    -   **BEHAVIOR:** The pipeline should continue processing other stocks even if a model for one specific stock fails to load.
    -   **SETUP:**
        -   Mock the database to return ['AAPL', 'MSFT'].
        -   Configure the mock `PredictionModel.load_model` to raise a "ModelNotFound" error for 'MSFT' but succeed for 'AAPL'.
    -   **ACTION:** Call `run_daily_predictions()`.
    -   **ASSERT:**
        -   Verify that a specific error for 'MSFT' was logged.
        -   Verify that the prediction process for 'AAPL' completed successfully (e.g., `store_prediction` was called for 'AAPL').
        -   Verify that the overall function does not crash.

## 2. Pseudocode Logic

```plaintext
FUNCTION run_daily_predictions():
    //-- TEST BEHAVIOR: Main function execution starts
    LOG "Starting daily prediction job."

    TRY
        //-- 1. Get all unique stocks from user watchlists
        //-- TEST BEHAVIOR: Should fetch a unique list of stock symbols from the database.
        LOG "Fetching all tracked stocks from user watchlists."
        all_tracked_stocks = DATABASE.query("SELECT DISTINCT symbol FROM WatchlistItems")

        IF all_tracked_stocks IS EMPTY THEN
            //-- TEST BEHAVIOR: Should log and exit if no stocks are tracked.
            LOG "No tracked stocks found in any watchlist. Exiting job."
            RETURN
        END IF

        LOG "Found " + length(all_tracked_stocks) + " unique stocks to process."

        //-- 2. Run the full data ingestion pipeline for the tracked stocks
        //-- TEST BEHAVIOR: Should trigger data ingestion for the list of stocks.
        LOG "Running data ingestion pipeline..."
        ingestion_result = run_ingestion_pipeline(stocks = all_tracked_stocks)
        IF ingestion_result IS FAILURE THEN
            LOG_ERROR "Data ingestion pipeline failed. Aborting daily job."
            RETURN
        END IF
        LOG "Data ingestion complete."

        //-- 3. Run the data processing pipeline
        //-- TEST BEHAVIOR: Should trigger data processing for the list of stocks.
        LOG "Running data processing pipeline..."
        processing_result = run_processing_pipeline(stocks = all_tracked_stocks)
        IF processing_result IS FAILURE THEN
            LOG_ERROR "Data processing pipeline failed. Aborting daily job."
            RETURN
        END IF
        LOG "Data processing complete."

        //-- 4. Generate and store predictions for each stock
        LOG "Starting prediction generation loop for each stock."
        FOR EACH stock_symbol IN all_tracked_stocks:
            LOG "Processing prediction for: " + stock_symbol
            TRY
                //-- 4a. Load the trained model for the stock
                //-- TEST BEHAVIOR: Should attempt to load a pre-trained model for the stock.
                prediction_model = PredictionModel.load_model(symbol = stock_symbol)

                IF prediction_model IS NULL THEN
                    //-- TEST BEHAVIOR: Should log an error and skip if a model is not found.
                    LOG_ERROR "Model for " + stock_symbol + " not found. Skipping prediction."
                    CONTINUE FOR //-- Move to the next stock
                END IF

                //-- 4b. Generate the new prediction
                //-- TEST BEHAVIOR: Should use the loaded model to generate a new prediction.
                LOG "Generating new prediction for " + stock_symbol
                latest_processed_data = DATABASE.query("SELECT * FROM ProcessedData WHERE symbol = " + stock_symbol + " ORDER BY date DESC LIMIT 1")
                prediction_result = prediction_model.predict(data = latest_processed_data)

                //-- 4c. Store the new prediction in the database
                //-- TEST BEHAVIOR: Should store the generated prediction in the database.
                LOG "Storing prediction for " + stock_symbol + " in the database."
                DATABASE.store_prediction(
                    symbol = stock_symbol,
                    signal = prediction_result.signal,
                    confidence = prediction_result.confidence,
                    timestamp = current_utc_time()
                )

                //-- 4d. Update the prediction cache
                //-- TEST BEHAVIOR: Should update the cache with the new prediction.
                LOG "Updating prediction cache for " + stock_symbol
                cache_payload = {
                    "symbol": stock_symbol,
                    "signal": prediction_result.signal,
                    "confidence": prediction_result.confidence,
                    "timestamp": current_utc_time()
                }
                PredictionCache.set(key = stock_symbol, value = cache_payload, ttl = 24 * 60 * 60) //-- 24-hour TTL

                LOG "Successfully processed prediction for: " + stock_symbol

            CATCH SpecificException AS model_exception
                //-- Handles errors during the loop for a single stock (e.g., model loading, prediction error)
                //-- TEST BEHAVIOR: Should log specific errors for a stock and continue with the next.
                LOG_ERROR "An error occurred while processing prediction for " + stock_symbol + ": " + model_exception.message
                //-- Continue to the next stock in the loop
            END TRY
        END FOR

        LOG "Daily prediction job finished successfully."

    CATCH GenericException AS global_exception
        //-- Handles errors at the pipeline level (e.g., database connection, pipeline failure)
        LOG_CRITICAL "A critical error occurred during the daily prediction job: " + global_exception.message
        //-- Optionally, send an alert (email, Slack, etc.)
        SEND_ALERT("Critical Failure in Daily Prediction Job", global_exception.message)
    END TRY

END FUNCTION