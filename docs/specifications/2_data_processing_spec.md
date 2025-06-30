# Specification: Data Processing and Feature Engineering

This document provides the technical specifications for the data processing and feature engineering components. This module is responsible for cleaning the raw data fetched by the ingestion module and transforming it into a feature-rich format suitable for the prediction models.

## 1. Overview

The data processing pipeline will consist of three main stages:
1.  **Tweet Processing:** Cleaning and preparing raw tweet text for sentiment analysis.
2.  **Price Data Processing:** Calculating technical indicators from historical price data.
3.  **Feature Combination:** Merging the processed price data and sentiment scores into a final feature set for the prediction model.

---

## 2. Tweet Processing

This component handles the cleaning and pre-processing of raw tweet text.

### 2.1. Class: `TweetProcessor`

A utility class for cleaning and tokenizing tweet text.

#### Methods

-   `clean_tweet(cls, text: str) -> str`
    -   **Description:** A static method that takes raw tweet text and performs cleaning operations. It removes URLs, user mentions (@), hashtags (#), special characters, and converts the text to lowercase.
    -   **Parameters:**
        -   `text` (str): The raw text of a tweet.
    -   **Returns:** `str`: The cleaned tweet text.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_clean_tweet
        # BEHAVIOR: Should remove all non-essential elements from the tweet text.
        # INPUT: "Check out $AAPL news! @user1 https://example.com #StockMarket"
        # EXPECTED_OUTPUT: "check out $aapl news! stockmarket"
        # ASSERT: The output matches the expected cleaned string.
        ```

-   `tokenize_and_remove_stopwords(cls, text: str, stopwords: set) -> list[str]`
    -   **Description:** A static method that tokenizes the cleaned text and removes common English stop words.
    -   **Parameters:**
        -   `text` (str): The cleaned tweet text.
        -   `stopwords` (set): A set of stop words to remove.
    -   **Returns:** `list[str]`: A list of meaningful tokens.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_tokenize_and_remove_stopwords
        # BEHAVIOR: Should split text into tokens and remove useless words.
        # INPUT: "this is a great stock"
        # SETUP: stopwords = {'this', 'is', 'a'}
        # EXPECTED_OUTPUT: ["great", "stock"]
        # ASSERT: The output list contains only the significant words.
        ```

---

## 3. Price Data Feature Engineering

This component calculates technical indicators from the historical price data.

### 3.1. Class: `FeatureEngineer`

A utility class for calculating financial technical indicators. It will operate on a pandas DataFrame.

#### Methods

-   `calculate_moving_average(cls, data: 'pd.DataFrame', window: int) -> 'pd.Series'`
    -   **Description:** A static method to calculate the Simple Moving Average (SMA) for the 'close' price.
    -   **Parameters:**
        -   `data` (pd.DataFrame): DataFrame containing historical price data with a 'close' column.
        -   `window` (int): The rolling window size (e.g., 20 for a 20-day SMA).
    -   **Returns:** `pd.Series`: A pandas Series containing the calculated SMA.

-   `calculate_rsi(cls, data: 'pd.DataFrame', window: int = 14) -> 'pd.Series'`
    -   **Description:** A static method to calculate the Relative Strength Index (RSI).
    -   **Parameters:**
        -   `data` (pd.DataFrame): DataFrame with a 'close' column.
        -   `window` (int): The window for RSI calculation. Defaults to 14.
    -   **Returns:** `pd.Series`: A pandas Series containing the RSI values.

-   `calculate_macd(cls, data: 'pd.DataFrame', fast_window: int = 12, slow_window: int = 26, signal_window: int = 9) -> tuple['pd.Series', 'pd.Series']`
    -   **Description:** A static method to calculate the Moving Average Convergence Divergence (MACD) and its signal line.
    -   **Parameters:**
        -   `data` (pd.DataFrame): DataFrame with a 'close' column.
        -   `fast_window` (int): The window for the fast EMA.
        -   `slow_window` (int): The window for the slow EMA.
        -   `signal_window` (int): The window for the MACD signal line.
    -   **Returns:** `tuple[pd.Series, pd.Series]`: A tuple containing the MACD line and the signal line.

-   `calculate_bollinger_bands(cls, data: 'pd.DataFrame', window: int = 20) -> tuple['pd.Series', 'pd.Series']`
    -   **Description:** A static method to calculate the upper and lower Bollinger Bands.
    -   **Parameters:**
        -   `data` (pd.DataFrame): DataFrame with a 'close' column.
        -   `window` (int): The window for the moving average and standard deviation.
    -   **Returns:** `tuple[pd.Series, pd.Series]`: A tuple containing the upper and lower band Series.

-   `add_all_features(cls, data: 'pd.DataFrame') -> 'pd.DataFrame'`
    -   **Description:** A static method that applies all feature engineering functions to the price data DataFrame and returns it with the new feature columns.
    -   **Parameters:**
        -   `data` (pd.DataFrame): The initial DataFrame with OHLCV data.
    -   **Returns:** `pd.DataFrame`: The DataFrame augmented with all technical indicator columns.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_add_all_features
        # BEHAVIOR: Should return a DataFrame with new columns for all calculated features.
        # SETUP: Create a sample DataFrame with 'close' price data.
        # ACTION: Call add_all_features on the sample data.
        # ASSERT: The returned DataFrame contains columns like 'SMA_20', 'RSI_14', 'MACD', etc.
        ```

---

## 4. Data Processing Orchestrator

This function orchestrates the entire data processing pipeline.

### 4.1. Function: `run_processing_pipeline(raw_data: dict) -> dict`

-   **Description:** This function takes the raw data dictionary from the ingestion pipeline. For each stock, it processes the tweets, calculates sentiment, aggregates daily sentiment, adds technical features to price data, and merges them. **Temporal Alignment Strategy:** All sentiment from tweets posted between market close on day `T-1` and market close on day `T` will be aggregated and assigned to trading day `T`. Market close is considered 4:00 PM EST.
-   **Parameters:**
    -   `raw_data` (dict): The dictionary output from `run_ingestion_pipeline`.
-   **Returns:** `dict`: A dictionary where keys are stock symbols and values are pandas DataFrames containing the final, processed features for each stock.
-   **TDD Anchor/Pseudocode Stub:**
    ```python
    # TEST: test_run_processing_pipeline
    # BEHAVIOR: Should process raw data and return a dictionary of feature-rich DataFrames.
    # SETUP: Create a sample raw_data dictionary with 'price_data' and 'tweet_data'.
    # MOCK: Mock the sentiment analysis model to return predefined scores.
    # ACTION: Call run_processing_pipeline with the sample data.
    # ASSERT: The output for each stock is a DataFrame.
    # ASSERT: The DataFrame contains both technical indicator columns and sentiment-based columns (e.g., 'daily_sentiment_score').

    # TEST: test_temporal_alignment_logic
    # BEHAVIOR: Should correctly align tweet sentiment to the corresponding trading day.
    # SETUP:
    #   - Price data for Monday, Tuesday.
    #   - Tweet 1: Monday @ 3:59 PM EST (belongs to Monday)
    #   - Tweet 2: Monday @ 4:01 PM EST (belongs to Tuesday)
    #   - Tweet 3: Saturday @ 10:00 AM EST (belongs to Monday)
    #   - Market Holiday: Assume Tuesday is a holiday, so no price data.
    #   - Tweet 4: Tuesday @ 11:00 AM EST (belongs to Wednesday)
    # MOCK: Mock sentiment analysis.
    # ACTION: Call run_processing_pipeline.
    # ASSERT:
    #   - Monday's sentiment score in the output DataFrame includes Tweet 1 and Tweet 3.
    #   - Tuesday's sentiment score includes Tweet 2.
    #   - Wednesday's sentiment score includes Tweet 4.
    ```