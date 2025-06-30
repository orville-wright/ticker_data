# Specification: Sentiment Analysis Model

This document outlines the technical specifications for the sentiment analysis model. The model will be responsible for analyzing the cleaned tweet text and assigning a sentiment score (positive, negative, neutral) to it.

## 1. Overview

The sentiment analysis component will be a class that encapsulates a fine-tuned BERT model. This class will handle loading the pre-trained model, tokenizing input text, performing inference, and returning a structured sentiment prediction. The Hugging Face `transformers` library will be the primary tool for this implementation.

---

## 2. Sentiment Analysis Model Class

### 2.1. Class: `SentimentAnalysisModel`

A class for performing sentiment analysis using a fine-tuned BERT model.

#### Properties

-   `model` (`transformers.PreTrainedModel`): The loaded pre-trained and fine-tuned BERT model for sequence classification.
-   `tokenizer` (`transformers.PreTrainedTokenizer`): The tokenizer corresponding to the BERT model.
-   `device` (str): The device to run the model on ('cuda' or 'cpu').

#### Methods

-   `__init__(self, model_name: str = 'ProsusAI/finbert')`
    -   **Description:** Initializes the sentiment analysis model by loading a pre-trained, finance-specific model and tokenizer from Hugging Face. It also determines the best available device for computation (GPU or CPU).
    -   **Parameters:**
        -   `model_name` (str): The identifier of the pre-trained model on Hugging Face Hub. Defaults to `ProsusAI/finbert`, a model specifically tuned for financial text.
    -   **Returns:** `None`

-   `predict_sentiment(self, text: str) -> dict`
    -   **Description:** Predicts the sentiment of a single piece of text.
    -   **Parameters:**
        -   `text` (str): The input text to analyze.
    -   **Returns:** `dict`: A dictionary containing the predicted label ('POSITIVE', 'NEGATIVE', 'NEUTRAL') and the confidence score. Example: `{'label': 'POSITIVE', 'score': 0.98}`.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_predict_sentiment_hawkish_is_negative
        # BEHAVIOR: Should correctly classify a nuanced, negative financial text.
        # SETUP: Initialize SentimentAnalysisModel with the FinBERT model.
        # INPUT: "Powell sounds hawkish, market is not going to like this."
        # EXPECTED_OUTPUT: A dictionary with label 'NEGATIVE'.
        # ASSERT: The 'label' in the returned dict is 'NEGATIVE'.

        # TEST: test_predict_sentiment_diamond_hands_is_positive
        # BEHAVIOR: Should correctly classify financial jargon as positive.
        # SETUP: Initialize SentimentAnalysisModel with the FinBERT model.
        # INPUT: "Diamond handing $GME all the way."
        # EXPECTED_OUTPUT: A dictionary with label 'POSITIVE'.
        # ASSERT: The 'label' in the returned dict is 'POSITIVE'.
        ```

-   `bulk_predict_sentiment(self, texts: list[str]) -> list[dict]`
    -   **Description:** Predicts the sentiment for a batch of texts efficiently.
    -   **Parameters:**
        -   `texts` (list[str]): A list of text strings to analyze.
    -   **Returns:** `list[dict]`: A list of prediction dictionaries, one for each input text.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_bulk_predict_sentiment
        # BEHAVIOR: Should return a list of sentiment predictions for a batch of texts.
        # SETUP: Initialize SentimentAnalysisModel.
        # INPUT: ["Stock is up", "Market is crashing"]
        # EXPECTED_OUTPUT_COUNT: 2
        # ASSERT: The returned list has the same number of elements as the input list.
        # ASSERT: The first element's label is 'POSITIVE' and the second is 'NEGATIVE'.
        ```

---

## 3. Sentiment Aggregation Function

This function will aggregate the individual tweet sentiments into a single daily score for each stock.

### 3.1. Function: `aggregate_daily_sentiment(sentiment_predictions: list[dict]) -> dict`

-   **Description:** This function takes a list of sentiment predictions for a given stock on a given day and aggregates them into a single score. It converts labels to a numerical scale (e.g., POSITIVE=1, NEUTRAL=0, NEGATIVE=-1) and calculates a weighted average based on the confidence scores.
-   **Parameters:**
    -   `sentiment_predictions` (list[dict]): A list of sentiment dictionaries, each from `SentimentAnalysisModel.predict_sentiment`.
-   **Returns:** `dict`: A dictionary containing the aggregated sentiment score and other metrics. Example: `{'daily_sentiment_score': 0.75, 'positive_count': 150, 'negative_count': 20}`.
-   **TDD Anchor/Pseudocode Stub:**
    ```python
    # TEST: test_aggregate_daily_sentiment
    # BEHAVIOR: Should correctly calculate an aggregated sentiment score.
    # INPUT: [
    #   {'label': 'POSITIVE', 'score': 0.9},
    #   {'label': 'POSITIVE', 'score': 0.8},
    #   {'label': 'NEGATIVE', 'score': 0.95}
    # ]
    # EXPECTED_OUTPUT_SCORE: (0.9 * 1 + 0.8 * 1 + 0.95 * -1) / (0.9 + 0.8 + 0.95) = 0.28
    # ASSERT: The 'daily_sentiment_score' is close to the expected value.