# Pseudocode: run_processing_pipeline

## FUNCTION `run_processing_pipeline(raw_data)`

### DESCRIPTION
Orchestrates the entire data processing pipeline. It takes raw data from the ingestion phase, processes tweets, calculates sentiment, aggregates sentiment according to a specific temporal alignment strategy, computes technical indicators for price data, and merges these data sources into a final feature set for each stock.

### INPUTS
- `raw_data` (Dictionary)-- A dictionary where keys are stock symbols. Each value is another dictionary containing 'price_data' (as a DataFrame) and 'tweet_data' (as a DataFrame).

### OUTPUTS
- `processed_data` (Dictionary)-- A dictionary where keys are stock symbols and values are DataFrames containing the final, processed features ready for model training.

### TDD ANCHORS

- **TEST**-- `test_run_processing_pipeline_happy_path`
  - **BEHAVIOR**-- Should correctly process a standard raw data dictionary and return a dictionary of feature-rich DataFrames.
  - **SETUP**-- Create a sample `raw_data` dictionary containing 'price_data' and 'tweet_data' for a single stock.
  - **MOCK**-- Mock the sentiment analysis model to return predefined, consistent scores. Mock the `FeatureEngineer` to return a predictable DataFrame with technical indicators.
  - **ACTION**-- Call `run_processing_pipeline` with the sample data.
  - **ASSERT**-- The output dictionary contains the stock symbol as a key.
  - **ASSERT**-- The value for the stock is a DataFrame.
  - **ASSERT**-- The DataFrame contains columns for technical indicators (e.g., 'SMA_20', 'RSI_14') and a 'daily_sentiment_score' column.

- **TEST**-- `test_temporal_alignment_logic`
  - **BEHAVIOR**-- Should correctly align tweet sentiment to the corresponding trading day based on market close times, weekends, and holidays.
  - **SETUP**--
    - Create price data for a Monday, Tuesday (holiday), and Wednesday.
    - Create Tweet 1-- Monday @ 3--59 PM EST (should be assigned to Monday).
    - Create Tweet 2-- Monday @ 4--01 PM EST (should be assigned to Tuesday, which is a holiday, so rolls to Wednesday).
    - Create Tweet 3-- Saturday @ 10--00 AM EST (should be assigned to the next trading day, Monday).
    - Create Tweet 4-- Tuesday @ 11--00 AM EST (holiday, should be assigned to Wednesday).
  - **MOCK**-- Mock the sentiment analysis model to return distinct scores for each tweet.
  - **ACTION**-- Call `run_processing_pipeline` with this specific setup.
  - **ASSERT**-- The 'daily_sentiment_score' for Monday in the output DataFrame is derived from Tweet 1 and Tweet 3.
  - **ASSERT**-- The output DataFrame has no row for the holiday (Tuesday).
  - **ASSERT**-- The 'daily_sentiment_score' for Wednesday is derived from Tweet 2 and Tweet 4.

### LOGIC

1.  **INITIALIZE** an empty dictionary `processed_data` to store the final results.
2.  **INITIALIZE** a `sentiment_analyzer` instance (e.g., load a pre-trained model).
3.  **INITIALIZE** a set of `stopwords` for text processing.
4.  **DEFINE** `market_close_hour` = 16 (4--00 PM).
5.  **DEFINE** `market_timezone` = 'America/New_York' (EST/EDT).
6.  **DEFINE** a list or set of `market_holidays`.

7.  **FOR EACH** `stock_symbol`, `data` in `raw_data.items()`--
    a.  **EXTRACT** `price_data_df` and `tweet_data_df` from `data`.
    b.  **INITIALIZE** `daily_sentiment` DataFrame as empty.

    c.  **IF** `tweet_data_df` is not empty--
        i.   //-- Stage 1-- Process Tweets and Calculate Raw Sentiment --//
        ii.  **CREATE** an empty list `tweet_sentiments`.
        iii. **FOR EACH** `tweet` in `tweet_data_df.rows`--
            1.  `cleaned_text` = CALL [`clean_tweet_pseudocode.md`](docs/pseudocode/data_processing/clean_tweet_pseudocode.md) with `tweet.text`.
            2.  `tokens` = CALL [`tokenize_and_remove_stopwords_pseudocode.md`](docs/pseudocode/data_processing/tokenize_and_remove_stopwords_pseudocode.md) with `cleaned_text` and `stopwords`.
            3.  **IF** `tokens` is not empty--
                a.  `sentiment_score` = CALL `sentiment_analyzer.predict(tokens)`.
                b.  **APPEND** a record `{timestamp, sentiment_score}` to `tweet_sentiments`.

        iv.  **IF** `tweet_sentiments` is not empty--
            1.  //-- Stage 2-- Temporal Alignment --//
            2.  **CREATE** `sentiment_df` from `tweet_sentiments`.
            3.  **CONVERT** `sentiment_df['timestamp']` to datetime objects, localized to `market_timezone`.
            4.  **CREATE** a new column `trading_day` in `sentiment_df`.
            5.  **FOR EACH** `row` in `sentiment_df`--
                a.  `tweet_timestamp` = `row['timestamp']`.
                b.  `assigned_date` = `tweet_timestamp.date()`.
                c.  **IF** `tweet_timestamp.hour` >= `market_close_hour`--
                    -   `assigned_date` = `assigned_date` + 1 day.
                d.  **WHILE** `assigned_date.weekday()` is Saturday/Sunday OR `assigned_date` is in `market_holidays`--
                    -   `assigned_date` = `assigned_date` + 1 day.
                e.  **SET** `row['trading_day']` = `assigned_date`.

            6.  //-- Stage 3-- Aggregate Daily Sentiment --//
            7.  `daily_sentiment` = **GROUP** `sentiment_df` by `trading_day`.
            8.  **AGGREGATE** `sentiment_score` for each group to get the mean, and name it `daily_sentiment_score`.
            9.  **RESET** index of `daily_sentiment` to make `trading_day` a column.

    d.  //-- Stage 4-- Add Technical Features to Price Data --//
    e.  `features_df` = CALL `FeatureEngineer.add_all_features(price_data_df)`. This function is assumed to add columns like SMA, RSI, etc.

    f.  //-- Stage 5-- Merge Sentiment and Price Features --//
    g.  **CONVERT** `features_df` index to date objects for merging.
    h.  **IF** `daily_sentiment` is not empty--
        i.   `final_df` = **MERGE** `features_df` with `daily_sentiment` using a left join on the date (`features_df.index` and `daily_sentiment.trading_day`).
        ii.  **FILL** any resulting `NaN` values in `daily_sentiment_score` with a neutral value (e.g., 0) or forward-fill.
    i.  **ELSE** (no tweets or no valid sentiment)--
        i.   `final_df` = `features_df`.
        ii.  **ADD** a `daily_sentiment_score` column to `final_df` and fill with 0.

    j.  **STORE** `final_df` in `processed_data` dictionary with `stock_symbol` as the key.

8.  **RETURN** `processed_data`.