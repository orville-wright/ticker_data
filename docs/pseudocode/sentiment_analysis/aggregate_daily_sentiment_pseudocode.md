# Pseudocode: aggregate_daily_sentiment

This document provides a detailed, language-agnostic pseudocode for the `aggregate_daily_sentiment` function, which aggregates a list of individual sentiment predictions into a single daily score.

## Function Signature

```
FUNCTION aggregate_daily_sentiment(sentiment_predictions: LIST of DICTIONARY) -> DICTIONARY
```

## Description

This function takes a list of sentiment predictions for a given stock on a given day and aggregates them into a single score. It converts sentiment labels to a numerical scale (e.g., POSITIVE=1, NEUTRAL=0, NEGATIVE=-1) and calculates a weighted average based on the confidence scores of each prediction.

## TDD Anchors

-   **TEST** `test_aggregate_daily_sentiment_happy_path`-- Behavior for a typical list of mixed sentiments.
-   **TEST** `test_aggregate_daily_sentiment_empty_list`-- Behavior when the input list is empty.
-   **TEST** `test_aggregate_daily_sentiment_all_positive`-- Behavior with only positive sentiments.
-   **TEST** `test_aggregate_daily_sentiment_all_negative`-- Behavior with only negative sentiments.
-   **TEST** `test_aggregate_daily_sentiment_all_neutral`-- Behavior with only neutral sentiments.
-   **TEST** `test_aggregate_daily_sentiment_zero_weights`-- Behavior if all confidence scores are zero, to prevent division by zero.
-   **TEST** `test_aggregate_daily_sentiment_single_prediction`-- Behavior with a single prediction in the list.

## Pseudocode

```plaintext
FUNCTION aggregate_daily_sentiment(sentiment_predictions)

  -- TDD Anchor-- test_aggregate_daily_sentiment_empty_list
  -- BEHAVIOR-- Should return a default dictionary with zero values if the input list is empty.
  -- SETUP-- None
  -- INPUT-- An empty list []
  -- EXPECTED_OUTPUT-- {'daily_sentiment_score'-- 0.0, 'positive_count'-- 0, 'negative_count'-- 0, 'neutral_count'-- 0, 'total_predictions'-- 0}
  -- ASSERT-- The returned dictionary matches the expected output.
  IF sentiment_predictions is NULL or is_empty(sentiment_predictions) THEN
    RETURN {
      "daily_sentiment_score"-- 0.0,
      "positive_count"-- 0,
      "negative_count"-- 0,
      "neutral_count"-- 0,
      "total_predictions"-- 0
    }
  END IF

  -- 1. Initialization
  INITIALIZE total_weighted_score = 0.0
  INITIALIZE total_weights = 0.0
  INITIALIZE positive_count = 0
  INITIALIZE negative_count = 0
  INITIALIZE neutral_count = 0

  -- Define the numerical mapping for sentiment labels
  DEFINE sentiment_map = {
    "POSITIVE"-- 1,
    "NEUTRAL"-- 0,
    "NEGATIVE"-- -1
  }

  -- 2. Loop and Aggregate
  -- TDD Anchor-- test_aggregate_daily_sentiment_happy_path
  -- BEHAVIOR-- Should correctly calculate a weighted average sentiment score from a mixed list.
  -- SETUP-- None
  -- INPUT-- [{'label'-- 'POSITIVE', 'score'-- 0.9}, {'label'-- 'NEGATIVE', 'score'-- 0.95}, {'label'-- 'POSITIVE', 'score'-- 0.8}]
  -- EXPECTED_OUTPUT_SCORE-- (1*0.9 + -1*0.95 + 1*0.8) / (0.9 + 0.95 + 0.8) approx 0.28
  -- ASSERT-- The 'daily_sentiment_score' is close to the expected value. positive_count is 2, negative_count is 1.
  FOR EACH prediction IN sentiment_predictions
    -- Get label and score from the prediction dictionary
    LET label = prediction["label"]
    LET score = prediction["score"]

    -- Convert text label to numerical value
    LET sentiment_value = sentiment_map[label]

    -- Calculate the score weighted by confidence
    LET weighted_score = sentiment_value * score

    -- Accumulate totals
    total_weighted_score = total_weighted_score + weighted_score
    total_weights = total_weights + score

    -- Increment counters for each sentiment type
    IF label == "POSITIVE" THEN
      positive_count = positive_count + 1
    ELSE IF label == "NEGATIVE" THEN
      negative_count = negative_count + 1
    ELSE IF label == "NEUTRAL" THEN
      neutral_count = neutral_count + 1
    END IF
  END FOR

  -- 3. Final Calculation
  INITIALIZE aggregated_score = 0.0

  -- TDD Anchor-- test_aggregate_daily_sentiment_zero_weights
  -- BEHAVIOR-- Should return 0.0 score if total weights are zero to avoid division by zero.
  -- SETUP-- None
  -- INPUT-- [{'label'-- 'POSITIVE', 'score'-- 0.0}, {'label'-- 'NEGATIVE', 'score'-- 0.0}]
  -- EXPECTED_OUTPUT_SCORE-- 0.0
  -- ASSERT-- The 'daily_sentiment_score' is exactly 0.0.
  IF total_weights > 0 THEN
    aggregated_score = total_weighted_score / total_weights
  END IF

  -- 4. Construct Result
  LET total_predictions_count = length(sentiment_predictions)

  LET result = {
    "daily_sentiment_score"-- aggregated_score,
    "positive_count"-- positive_count,
    "negative_count"-- negative_count,
    "neutral_count"-- neutral_count,
    "total_predictions"-- total_predictions_count
  }

  -- 5. Return
  RETURN result

END FUNCTION