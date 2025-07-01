import pytest
import torch
from unittest.mock import patch, MagicMock

# These imports will fail until the implementation is created in `ml_sentiment.py`,
# which is the correct behavior for TDD.
try:
    from ml_sentiment import SentimentAnalysisModel, aggregate_daily_sentiment
except ImportError:
    # Define placeholder classes/functions if the module doesn't exist yet
    # This allows the test file to be syntactically valid, even if the tests will fail.
    class SentimentAnalysisModel:
        def __init__(self, model_name: str):
            pass
        def predict_sentiment(self, text: str):
            pass
        def bulk_predict_sentiment(self, texts: list):
            pass

    def aggregate_daily_sentiment(predictions: list):
        pass

# Test Case 1: Model Initialization (SAM-INIT-001)
# To test the __init__ method, we patch the collaborators in the module where they are *used*.
@patch('ml_sentiment.torch.cuda.is_available', return_value=False)
@patch('ml_sentiment.AutoModelForSequenceClassification.from_pretrained')
@patch('ml_sentiment.AutoTokenizer.from_pretrained')
def test_model_initialization(mock_tokenizer_fp, mock_model_fp, mock_cuda_available):
    """
    Verifies that the constructor calls the Hugging Face library to load the
    specified model and tokenizer and correctly selects the computation device.
    """
    # Arrange
    mock_model_instance = MagicMock()
    mock_model_fp.return_value = mock_model_instance

    # Act
    SentimentAnalysisModel(model_name='ProsusAI/finbert')

    # Assert
    mock_tokenizer_fp.assert_called_once_with('ProsusAI/finbert')
    mock_model_fp.assert_called_once_with('ProsusAI/finbert')
    mock_cuda_available.assert_called_once()
    mock_model_instance.to.assert_called_once_with('cpu')

@pytest.fixture
def mocked_sentiment_model():
    """
    Provides a SentimentAnalysisModel instance with its tokenizer and model
    attributes pre-mocked for interaction testing.
    """
    with patch('ml_sentiment.AutoModelForSequenceClassification.from_pretrained'), \
         patch('ml_sentiment.AutoTokenizer.from_pretrained'):

        model = SentimentAnalysisModel(model_name='ProsusAI/finbert')

        # Replace collaborators with mocks
        model.tokenizer = MagicMock()
        model.model = MagicMock()

        # Configure the mock model's config to map IDs to labels
        model.model.config.id2label = {0: 'NEGATIVE', 1: 'POSITIVE', 2: 'NEUTRAL'}

        return model

# Test Case 2: Positive Sentiment Prediction (SAM-PRED-001)
def test_predict_sentiment_positive(mocked_sentiment_model):
    """
    Ensures that a text with known positive financial jargon is
    correctly classified as 'POSITIVE'.
    """
    # Arrange
    text = "Diamond handing $GME all the way."
    mocked_sentiment_model.tokenizer.return_value = {
        'input_ids': torch.tensor([[101]]), 'attention_mask': torch.tensor([[1]])
    }
    # Mock model to return logits for a 'POSITIVE' classification (index 1)
    mocked_sentiment_model.model.return_value.logits = torch.tensor([[-1.5, 2.5, 0.5]])

    # Act
    result = mocked_sentiment_model.predict_sentiment(text)

    # Assert: AI Verifiable Criterion
    assert result['label'] == 'POSITIVE'
    mocked_sentiment_model.tokenizer.assert_called_once_with(text, return_tensors='pt', padding=True, truncation=True)

# Test Case 3: Negative Sentiment Prediction (SAM-PRED-002)
def test_predict_sentiment_negative(mocked_sentiment_model):
    """
    Ensures a nuanced, negative financial text is correctly classified as 'NEGATIVE'.
    """
    # Arrange
    text = "Powell sounds hawkish, market is not going to like this."
    mocked_sentiment_model.tokenizer.return_value = {
        'input_ids': torch.tensor([[102]]), 'attention_mask': torch.tensor([[1]])
    }
    # Mock model to return logits for a 'NEGATIVE' classification (index 0)
    mocked_sentiment_model.model.return_value.logits = torch.tensor([[2.5, -1.5, 0.5]])

    # Act
    result = mocked_sentiment_model.predict_sentiment(text)

    # Assert: AI Verifiable Criterion
    assert result['label'] == 'NEGATIVE'
    mocked_sentiment_model.tokenizer.assert_called_once_with(text, return_tensors='pt', padding=True, truncation=True)

# Test Case 4: Bulk Sentiment Prediction (SAM-BULK-001)
def test_bulk_predict_sentiment(mocked_sentiment_model):
    """
    Verifies that the method correctly processes a list of texts and returns
    a list of sentiment predictions of the same length.
    """
    # Arrange
    texts = ["Stock is up", "Market is crashing"]
    mocked_sentiment_model.tokenizer.return_value = {
        'input_ids': torch.tensor([[101], [102]]), 'attention_mask': torch.tensor([[1], [1]])
    }
    # Mock model to return a batch of logits for POSITIVE and NEGATIVE
    mocked_sentiment_model.model.return_value.logits = torch.tensor([
        [-1.5, 2.5, 0.5],
        [2.5, -1.5, 0.5]
    ])

    # Act
    results = mocked_sentiment_model.bulk_predict_sentiment(texts)

    # Assert: AI Verifiable Criterion
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]['label'] == 'POSITIVE'
    assert results[1]['label'] == 'NEGATIVE'
    mocked_sentiment_model.tokenizer.assert_called_once_with(texts, return_tensors='pt', padding=True, truncation=True)

# Test Case 5: Sentiment Aggregation (ADS-AGG-001)
def test_aggregate_daily_sentiment():
    """
    Ensures the function correctly calculates a weighted average sentiment score
    and counts positive/negative/neutral predictions.
    """
    # Arrange
    predictions = [
        {'label': 'POSITIVE', 'score': 0.9},
        {'label': 'POSITIVE', 'score': 0.8},
        {'label': 'NEGATIVE', 'score': 0.95},
        {'label': 'NEUTRAL', 'score': 0.99}
    ]
    # Expected score: (1*0.9 + 1*0.8 + -1*0.95 + 0*0.99) / (0.9 + 0.8 + 0.95 + 0.99)
    expected_score = 0.75 / 3.64

    # Act
    result = aggregate_daily_sentiment(predictions)

    # Assert: AI Verifiable Criterion
    assert result['daily_sentiment_score'] == pytest.approx(expected_score)
    assert result['positive_count'] == 2
    assert result['negative_count'] == 1
    assert result['neutral_count'] == 1

# Test Case 6: Invalid Model Name (SAM-INIT-002)
def test_model_initialization_invalid_model():
    """
    Verifies that a ValueError is raised if an unsupported model name is provided.
    """
    with pytest.raises(ValueError, match="Only 'ProsusAI/finbert' model is allowed."):
        SentimentAnalysisModel(model_name='unsupported/model')

# Test Case 7: Resource Exhaustion Limit (SAM-BULK-002)
def test_bulk_predict_sentiment_too_many_texts(mocked_sentiment_model):
    """
    Verifies that a ValueError is raised if the input list of texts exceeds the
    maximum allowed size.
    """
    # Arrange
    texts = ["text"] * 1001

    # Act & Assert
    with pytest.raises(ValueError, match="Cannot process more than 1000 texts at a time."):
        mocked_sentiment_model.bulk_predict_sentiment(texts)