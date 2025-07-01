# Test Plan: Data Processing Pipeline

## 1. Document Overview

This document outlines the granular testing strategy for the **Data Processing Pipeline** feature. The plan is designed to ensure that all components responsible for cleaning, transforming, and enriching raw data function as specified and meet their AI-verifiable end results.

This plan adheres to the **London School of TDD**, emphasizing interaction-based testing. Tests will verify the observable behavior of units by mocking their collaborators, rather than inspecting internal state. The goal is to confirm that each unit correctly communicates with its dependencies to produce the desired outcome.

**AI Verifiable Goal:** The creation and existence of this test plan document at [`docs/test-plans/data_processing_pipeline_test_plan.md`](docs/test-plans/data_processing_pipeline_test_plan.md).

## 2. Scope of Testing

This test plan covers the following components as defined in the [`docs/specifications/2_data_processing_spec.md`](docs/specifications/2_data_processing_spec.md):

*   **`TweetProcessor` Class:** Methods for cleaning and tokenizing tweet text.
*   **`FeatureEngineer` Class:** Methods for calculating all financial technical indicators.
*   **`run_processing_pipeline` Function:** The main orchestrator that combines tweet processing, feature engineering, and sentiment alignment.

The tests defined herein are designed to validate the following AI-Verifiable End Results from the [`docs/primary_project_planning_document.md`](docs/primary_project_planning_document.md):
*   `The unit tests test_clean_tweet and test_tokenize_and_remove_stopwords pass successfully.`
*   `The unit test test_add_all_features passes, confirming all technical indicators are added to the DataFrame.`
*   `The unit test test_run_processing_pipeline passes, confirming the function correctly orchestrates cleaning, feature engineering, and sentiment aggregation.`

## 3. Recursive Testing (Regression) Strategy

A robust recursive testing strategy is crucial for maintaining stability as the system evolves.

**Triggers for Regression Testing:**
1.  **Post-Merge to Main Branch:** The full test suite for this module (`tests/functional/test_data_processing.py`) will be executed automatically via a CI/CD pipeline hook after any pull request is merged into the `main` branch.
2.  **Dependency Updates:** If any core data structures or the interfaces of collaborated-with modules (e.g., `SentimentAnalysisModel`) change, the relevant integration-style tests within this plan must be run.
3.  **Refactoring:** Any refactoring within the `data_processing` module, even if it doesn't change public method signatures, will trigger the full suite for this module.
4.  **Pre-Release Candidate Build:** The entire project's test suite, including these tests, will be run before tagging a new release candidate to ensure system-wide integrity.

**Test Prioritization & Selection:**
*   **Tier 1 (Critical Path):** All "happy path" tests for public-facing methods (`clean_tweet`, `add_all_features`, `run_processing_pipeline`). These will be tagged `@critical` and run on every commit to a feature branch.
*   **Tier 2 (Edge Cases & Validation):** Tests for input validation, error handling, and specific edge cases (e.g., empty inputs, data with NaNs). These will be run on pull requests.
*   **Tier 3 (Full Suite):** All tests for the module. This is the default for post-merge and pre-release triggers.

**AI Verifiable Completion Criterion:** The CI/CD pipeline configuration is updated to include a job that executes the test suite defined in this plan, triggered on merges to the `main` branch.

---

## 4. Test Cases

### 4.1. `TweetProcessor` Class

#### 4.1.1. `clean_tweet` Method

*   **Target AI Verifiable End Result:** `The unit tests test_clean_tweet... pass successfully.`
*   **Testing Approach (London School):** This is a pure function with no collaborators, so testing focuses on direct input/output validation.
*   **Test Cases (derived from TDD Anchors in [`clean_tweet_pseudocode.md`](docs/pseudocode/data_processing/clean_tweet_pseudocode.md)):**
    *   **`test_clean_tweet_happy_path`:**
        *   **Description:** Verifies the removal of URLs, mentions, and hashtag symbols, and converts text to lowercase.
        *   **Input:** `"Check out $AAPL news! @user1 https://example.com #StockMarket"`
        *   **Observable Outcome:** The method returns the exact string `"check out $aapl news! stockmarket"`.
        *   **AI Verifiable Criterion:** An assertion `assert result == "check out $aapl news! stockmarket"` passes.
    *   **`test_clean_tweet_empty_string`:**
        *   **Description:** Ensures the method handles empty input gracefully.
        *   **Input:** `""`
        *   **Observable Outcome:** The method returns `""`.
        *   **AI Verifiable Criterion:** An assertion `assert result == ""` passes.
    *   **`test_clean_tweet_retains_dollar_sign`:**
        *   **Description:** Ensures the `$` symbol, crucial for cashtags, is not removed.
        *   **Input:** `"$TSLA to the moon! #tesla"`
        *   **Observable Outcome:** The method returns `"$tsla to the moon! tesla"`.
        *   **AI Verifiable Criterion:** An assertion `assert result == "$tsla to the moon! tesla"` passes.
    *   **`test_clean_tweet_multiple_elements`:**
        *   **Description:** Ensures multiple occurrences of elements are cleaned correctly.
        *   **Input:** `"@person1 says #stocks are #awesome. @person2 agrees. See http://a.co"`
        *   **Observable Outcome:** The method returns `"says stocks are awesome. agrees. see"`.
        *   **AI Verifiable Criterion:** An assertion `assert result == "says stocks are awesome. agrees. see"` passes.

#### 4.1.2. `tokenize_and_remove_stopwords` Method

*   **Target AI Verifiable End Result:** `The unit tests ...and test_tokenize_and_remove_stopwords pass successfully.`
*   **Testing Approach (London School):** Pure function, direct input/output validation.
*   **Test Cases (derived from TDD Anchors in [`tokenize_and_remove_stopwords_pseudocode.md`](docs/pseudocode/data_processing/tokenize_and_remove_stopwords_pseudocode.md)):**
    *   **`test_tokenize_and_remove_stopwords_happy_path`:**
        *   **Description:** Verifies tokenization and removal of common words.
        *   **Input:** `text="this is a great stock"`, `stopwords={'this', 'is', 'a'}`
        *   **Observable Outcome:** The method returns the list `['great', 'stock']`.
        *   **AI Verifiable Criterion:** An assertion `assert result == ['great', 'stock']` passes.
    *   **`test_tokenize_and_remove_stopwords_all_stopwords`:**
        *   **Description:** Verifies that an empty list is returned if all words are stopwords.
        *   **Input:** `text="this is it"`, `stopwords={'this', 'is', 'it'}`
        *   **Observable Outcome:** The method returns `[]`.
        *   **AI Verifiable Criterion:** An assertion `assert result == []` passes.
    *   **`test_tokenize_and_remove_stopwords_empty_string`:**
        *   **Description:** Ensures the method handles an empty input string gracefully.
        *   **Input:** `text=""`, `stopwords={'a', 'the'}`
        *   **Observable Outcome:** The method returns `[]`.
        *   **AI Verifiable Criterion:** An assertion `assert result == []` passes.

### 4.2. `FeatureEngineer` Class

#### 4.2.1. `add_all_features` Method

*   **Target AI Verifiable End Result:** `The unit test test_add_all_features passes, confirming all technical indicators are added to the DataFrame.`
*   **Testing Approach (London School):** The `add_all_features` method collaborates with the individual indicator calculation methods (`calculate_moving_average`, `calculate_rsi`, etc.). These collaborators will be mocked to isolate the testing of the `add_all_features` orchestration logic.
*   **Test Cases:**
    *   **`test_add_all_features_orchestration`:**
        *   **Description:** Verifies that `add_all_features` calls all required underlying indicator calculation methods.
        *   **Collaborators to Mock:**
            *   `FeatureEngineer.calculate_moving_average`
            *   `FeatureEngineer.calculate_rsi`
            *   `FeatureEngineer.calculate_macd`
            *   `FeatureEngineer.calculate_bollinger_bands`
        *   **Setup:** Create a sample pandas DataFrame with a 'close' column. Configure each mock to return a predictable pandas Series of the same index.
        *   **Action:** Call `FeatureEngineer.add_all_features` with the sample DataFrame.
        *   **Observable Outcome:** Each mocked collaborator method is called exactly once with the correct arguments. The returned DataFrame contains new columns corresponding to the data returned by the mocks (e.g., 'SMA_20', 'RSI_14', 'MACD', 'MACD_signal', 'BB_upper', 'BB_lower').
        *   **AI Verifiable Criterion:** Assertions for `mock.assert_called_once()` for each collaborator pass. Assertions verifying the presence of the new columns in the output DataFrame pass.

    *   **`test_indicator_calculations_integration`:**
        *   **Description:** This is an integration-style test that verifies the actual calculations without mocking the individual methods. It uses a known dataset with pre-calculated "golden" values.
        *   **Setup:** Load a small, static dataset (e.g., from a CSV file) where the correct indicator values are known for a specific date.
        *   **Action:** Call `FeatureEngineer.add_all_features` on this dataset.
        *   **Observable Outcome:** The values in the resulting indicator columns for the specific date match the known golden values within a small tolerance.
        *   **AI Verifiable Criterion:** An assertion `pd.testing.assert_frame_equal(result_df, expected_golden_df)` or similar element-wise assertions pass.

### 4.3. `run_processing_pipeline` Function

*   **Target AI Verifiable End Result:** `The unit test test_run_processing_pipeline passes...`
*   **Testing Approach (London School):** This function is a high-level orchestrator. Its key collaborators are `TweetProcessor`, `SentimentAnalysisModel`, and `FeatureEngineer`. These will be mocked to test the orchestration logic in isolation.

*   **Test Cases:**
    *   **`test_run_processing_pipeline_orchestration`:**
        *   **Description:** Verifies the overall workflow of the pipeline for a single stock.
        *   **Collaborators to Mock:**
            *   `TweetProcessor.clean_tweet`
            *   `TweetProcessor.tokenize_and_remove_stopwords`
            *   `SentimentAnalysisModel.predict` (or `bulk_predict`)
            *   `FeatureEngineer.add_all_features`
        *   **Setup:** Create a sample `raw_data` dictionary with 'price_data' and 'tweet_data'. Configure mocks to return predictable values (e.g., `clean_tweet` returns "cleaned", `predict` returns 0.8, `add_all_features` returns a DataFrame with an 'SMA_20' column).
        *   **Action:** Call `run_processing_pipeline` with the sample data.
        *   **Observable Outcome:** The mocks for `TweetProcessor`, `SentimentAnalysisModel`, and `FeatureEngineer` are called. The returned dictionary contains a key for the stock, and its value is a DataFrame containing columns from the `FeatureEngineer` mock and a `daily_sentiment_score` column.
        *   **AI Verifiable Criterion:** `mock.assert_called()` passes for each collaborator. Assertions confirm the structure and content of the final DataFrame.

    *   **`test_temporal_alignment_logic`:**
        *   **Description:** Verifies that tweet sentiment is correctly assigned to trading days, accounting for market close, weekends, and holidays. This is a critical business logic test.
        *   **Collaborators to Mock:** `SentimentAnalysisModel.predict`
        *   **Setup (from spec):**
            *   Price data for Monday, Wednesday.
            *   Tweet 1: Monday @ 3:59 PM EST (sentiment 0.5)
            *   Tweet 2: Monday @ 4:01 PM EST (sentiment 0.8)
            *   Tweet 3: Saturday @ 10:00 AM EST (sentiment -0.4)
            *   Define Tuesday as a market holiday.
        *   **Action:** Call `run_processing_pipeline`.
        *   **Observable Outcome:** The final DataFrame has a `daily_sentiment_score` for Monday calculated from Tweets 1 and 3 (avg = 0.05). The score for Wednesday is calculated from Tweet 2 (avg = 0.8). There is no row for Tuesday.
        *   **AI Verifiable Criterion:** Assertions checking the specific `daily_sentiment_score` values for the Monday and Wednesday rows pass. An assertion confirms Tuesday's date is not in the DataFrame's index.
