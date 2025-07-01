# Test Plan: Sentiment Analysis Model

---

## 1. Document Overview

### 1.1. Purpose
This document provides a detailed, granular test plan for the `Sentiment Analysis Model` feature. It outlines the testing strategy, scope, resources, and specific test cases required to verify its functionality and ensure it meets the project's requirements.

### 1.2. Scope
This test plan covers the unit and integration testing of the `SentimentAnalysisModel` class and the `aggregate_daily_sentiment` function as defined in the feature specification. It focuses on verifying the interactions and observable outcomes of these components in isolation.

### 1.3. Objectives
- Ensure the `SentimentAnalysisModel` class correctly loads the specified model, processes text, and predicts sentiment for single and bulk inputs.
- Verify that the `aggregate_daily_sentiment` function correctly calculates a weighted average score from a list of predictions.
- Confirm that all tests are designed to validate the specific **AI-Verifiable End Results** outlined in the [`docs/primary_project_planning_document.md`](docs/primary_project_planning_document.md).
- Establish a clear, actionable plan for developers and AI agents to implement the tests following London School of TDD principles.

---

## 2. Test Scope & AI Verifiable Outcomes

This test plan is designed to directly validate the following AI-Verifiable End Results from the **Phase 1.2: Sentiment and Prediction Models** section of the primary project planning document:

- **`Implement the SentimentAnalysisModel class`**: Verified when the unit tests `test_predict_sentiment_positive`, `test_predict_sentiment_negative`, and `test_bulk_predict_sentiment` all pass successfully.
- **`Implement the aggregate_daily_sentiment function`**: Verified when the unit test `test_aggregate_daily_sentiment` passes, ensuring the weighted average score is calculated correctly.

---

## 3. Test Strategy

### 3.1. Methodology: London School of TDD
The testing approach will strictly adhere to the **London School of TDD (Interaction-Based Testing)**. This means:
- **Focus on Behavior, Not State:** Tests will verify that a unit sends the correct messages (i.e., calls methods) to its collaborators and produces the correct, observable output. The internal state of the unit under test (UUT) is not the primary focus.
- **Mocking Collaborators:** All external dependencies (collaborators) will be mocked. For the `SentimentAnalysisModel`, the primary collaborators are the components from the Hugging Face `transformers` library (`AutoModelForSequenceClassification`, `AutoTokenizer`) and `torch`. These will be replaced with mock objects to isolate the `SentimentAnalysisModel`'s own logic and to control the data returned by the collaborators during tests.

### 3.2. Recursive Testing (Regression) Strategy
A multi-layered regression strategy will be employed to ensure ongoing stability as the codebase evolves towards passing high-level acceptance tests.

- **Triggers for Re-running Tests:**
  - **On Every Commit (Pre-push hook):** Run a "Core Functionality" subset of tests.
  - **On Pull Request to `main`/`develop`:** Run the "Full Regression" suite for this feature.
  - **After Dependency Updates:** Run the "Full Regression" suite.
  - **Nightly Builds:** Run the entire project's test suite, including these tests.

- **Test Tagging and Prioritization:**
  - **`Core Functionality`:** Tests that cover the primary, non-edge-case paths. For this feature, this includes `test_predict_sentiment_positive`, `test_predict_sentiment_negative`, and `test_aggregate_daily_sentiment_basic`.
  - **`Full Regression`:** All unit tests defined in this plan, including edge cases and bulk operations.
  - **`Integration`:** Tests that might involve interactions with other real components (though none are defined in this specific unit test plan).

- **AI-Verifiable Completion Criterion:** The regression testing strategy is considered implemented when the CI/CD pipeline configuration is updated to execute tests based on these triggers and tags.

---

## 4. Test Environment & Data

- **Framework:** `pytest`
- **Mocking Library:** `unittest.mock`
- **Test Data:**
  - **Input Text:** A collection of strings representing financial tweets, including positive, negative, neutral, and jargon-filled examples as specified in the TDD Anchors.
  - **Mock Model Output:** Mocked tensor objects representing model logits, configured to produce desired outcomes when processed by the tested code.
  - **Mock Tokenizer Output:** Mocked dictionaries representing tokenized inputs (`input_ids`, `attention_mask`).

---

## 5. Test Cases

### 5.1. `SentimentAnalysisModel` Class

#### Test Case 1: Model Initialization
- **Test Case ID:** `SAM-INIT-001`
- **Targeted AI Verifiable End Result:** Prerequisite for all `SentimentAnalysisModel` tests.
- **Unit Under Test (UUT):** `SentimentAnalysisModel.__init__`
- **Test Description:** Verifies that the constructor calls the Hugging Face library to load the specified model and tokenizer and correctly selects the computation device.
- **Collaborators to Mock:**
  - `transformers.AutoModelForSequenceClassification.from_pretrained`
  - `transformers.AutoTokenizer.from_pretrained`
  - `torch.cuda.is_available`
- **Test Steps:**
  1. **Arrange:** Mock `torch.cuda.is_available` to return `False`. Mock the `from_pretrained` methods for the model and tokenizer.
  2. **Act:** Instantiate `SentimentAnalysisModel(model_name='test-model')`.
  3. **Assert:**
     - Verify `AutoTokenizer.from_pretrained` was called once with `'test-model'`.
     - Verify `AutoModelForSequenceClassification.from_pretrained` was called once with `'test-model'`.
     - Verify the `model.to` method was called with `'cpu'`.
- **Recursive Testing Scope:** `Full Regression`

#### Test Case 2: Positive Sentiment Prediction
- **Test Case ID:** `SAM-PRED-001`
- **Targeted AI Verifiable End Result:** `test_predict_sentiment_positive` passes.
- **Unit Under Test (UUT):** `SentimentAnalysisModel.predict_sentiment`
- **TDD Anchor:** `test_predict_sentiment_diamond_hands_is_positive`
- **Test Description:** Ensures that a text with known positive financial jargon is correctly classified as 'POSITIVE'.
- **Collaborators to Mock:** `self.tokenizer`, `self.model`
- **Test Steps:**
  1. **Arrange:**
     - Instantiate `SentimentAnalysisModel`.
     - Mock the `tokenizer` to return a sample token dictionary.
     - Mock the `model` to return a logit tensor that results in a 'POSITIVE' classification (e.g., `torch.tensor([[-1.5, 2.5, 0.5]])`). The model's config will map index 1 to the 'POSITIVE' label.
     - Define input text: `"Diamond handing $GME all the way."`
  2. **Act:** Call `predict_sentiment(text)`.
  3. **Assert:**
     - Verify the returned dictionary's `'label'` key has a value of `'POSITIVE'`.
     - **AI Verifiable Criterion:** The assertion `result['label'] == 'POSITIVE'` passes.
- **Recursive Testing Scope:** `Core Functionality`

#### Test Case 3: Negative Sentiment Prediction
- **Test Case ID:** `SAM-PRED-002`
- **Targeted AI Verifiable End Result:** `test_predict_sentiment_negative` passes.
- **Unit Under Test (UUT):** `SentimentAnalysisModel.predict_sentiment`
- **TDD Anchor:** `test_predict_sentiment_hawkish_is_negative`
- **Test Description:** Ensures a nuanced, negative financial text is correctly classified as 'NEGATIVE'.
- **Collaborators to Mock:** `self.tokenizer`, `self.model`
- **Test Steps:**
  1. **Arrange:**
     - Instantiate `SentimentAnalysisModel`.
     - Mock the `tokenizer` and `model` as in the positive test, but configure the mock model to return logits indicating a 'NEGATIVE' result (e.g., `torch.tensor([[2.5, -1.5, 0.5]])`). The model's config will map index 0 to the 'NEGATIVE' label.
     - Define input text: `"Powell sounds hawkish, market is not going to like this."`
  2. **Act:** Call `predict_sentiment(text)`.
  3. **Assert:**
     - Verify the returned dictionary's `'label'` key has a value of `'NEGATIVE'`.
     - **AI Verifiable Criterion:** The assertion `result['label'] == 'NEGATIVE'` passes.
- **Recursive Testing Scope:** `Core Functionality`

#### Test Case 4: Bulk Sentiment Prediction
- **Test Case ID:** `SAM-BULK-001`
- **Targeted AI Verifiable End Result:** `test_bulk_predict_sentiment` passes.
- **Unit Under Test (UUT):** `SentimentAnalysisModel.bulk_predict_sentiment`
- **TDD Anchor:** `test_bulk_predict_sentiment`
- **Test Description:** Verifies that the method correctly processes a list of texts and returns a list of sentiment predictions of the same length.
- **Collaborators to Mock:** `self.tokenizer`, `self.model`
- **Test Steps:**
  1. **Arrange:**
     - Instantiate `SentimentAnalysisModel`.
     - Configure the mock `tokenizer` to handle a list of strings.
     - Configure the mock `model` to return a batch of logits (e.g., `torch.tensor([[ -1.5, 2.5, 0.5], [2.5, -1.5, 0.5]])`).
     - Define input texts: `["Stock is up", "Market is crashing"]`.
  2. **Act:** Call `bulk_predict_sentiment(texts)`.
  3. **Assert:**
     - Verify the returned value is a list of length 2.
     - Verify the first element's label is 'POSITIVE'.
     - Verify the second element's label is 'NEGATIVE'.
     - **AI Verifiable Criterion:** Assertions for list length and correct labels all pass.
- **Recursive Testing Scope:** `Full Regression`

### 5.2. `aggregate_daily_sentiment` Function

#### Test Case 5: Sentiment Aggregation
- **Test Case ID:** `ADS-AGG-001`
- **Targeted AI Verifiable End Result:** `test_aggregate_daily_sentiment` passes.
- **Unit Under Test (UUT):** `aggregate_daily_sentiment`
- **TDD Anchor:** `test_aggregate_daily_sentiment`
- **Test Description:** Ensures the function correctly calculates a weighted average sentiment score and counts positive/negative predictions.
- **Collaborators to Mock:** None (pure function).
- **Test Steps:**
  1. **Arrange:**
     - Create the input list of prediction dictionaries:
       ```python
       [
         {'label': 'POSITIVE', 'score': 0.9},
         {'label': 'POSITIVE', 'score': 0.8},
         {'label': 'NEGATIVE', 'score': 0.95},
         {'label': 'NEUTRAL', 'score': 0.99}
       ]
       ```
     - Calculate the expected score: `(1*0.9 + 1*0.8 + -1*0.95 + 0*0.99) / (0.9 + 0.8 + 0.95 + 0.99) = 0.75 / 3.64 ≈ 0.206`
  2. **Act:** Call `aggregate_daily_sentiment(predictions)`.
  3. **Assert:**
     - Verify the `'daily_sentiment_score'` is approximately `0.206`.
     - Verify `'positive_count'` is `2`.
     - Verify `'negative_count'` is `1`.
     - Verify `'neutral_count'` is `1`.
     - **AI Verifiable Criterion:** Assertions for the score (using `pytest.approx`) and counts all pass.
- **Recursive Testing Scope:** `Core Functionality`

---

## 6. AI Verifiable Completion of This Plan

The primary AI-verifiable completion criterion for this task is the successful creation and saving of this document at the path [`docs/test-plans/sentiment_analysis_model_test_plan.md`](docs/test-plans/sentiment_analysis_model_test_plan.md). Furthermore, every test case defined herein contains its own explicit, AI-verifiable assertion criterion, ensuring that subsequent testing agents have a clear, machine-readable goal for test implementation.