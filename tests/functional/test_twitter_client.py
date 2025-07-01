import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
from unittest.mock import patch, MagicMock, ANY
from requests.exceptions import HTTPError, RequestException

from data_ingestion.twitter_client import TwitterClient

class TestTwitterClient:
    """
    Test suite for the optimized TwitterClient class.
    """

    BEARER_TOKEN = "test_bearer_token"
    TICKER = "AAPL"
    QUERY = f"#{TICKER} lang:en -is:retweet"

    SUCCESS_PAYLOAD = {
        "data": [
            {"id": "123", "text": f"Great news for ${TICKER}!"},
            {"id": "456", "text": f"Selling my ${TICKER} stock."},
        ],
        "meta": {"result_count": 2}
    }

    ERROR_PAYLOAD_400 = {
        "title": "Invalid Request",
        "detail": "Invalid 'query' parameter",
    }

    @pytest.fixture
    def mock_session(self):
        """Fixture to mock requests.Session."""
        with patch('data_ingestion.twitter_client.requests.Session') as MockSession:
            yield MockSession.return_value

    @pytest.fixture
    def mock_retry(self):
        """Fixture to mock urllib3.util.retry.Retry."""
        with patch('data_ingestion.twitter_client.Retry') as MockRetry:
            yield MockRetry

    @pytest.fixture
    def mock_adapter(self):
        """Fixture to mock requests.adapters.HTTPAdapter."""
        with patch('data_ingestion.twitter_client.HTTPAdapter') as MockAdapter:
            yield MockAdapter

    @patch('data_ingestion.twitter_client.requests.Session')
    def test_constructor_configures_retry_mechanism(self, MockSession, mock_retry, mock_adapter):
        """
        Verifies that the constructor correctly configures and mounts the HTTPAdapter
        with the specified retry strategy.
        """
        mock_session_instance = MockSession.return_value
        client = TwitterClient(
            bearer_token=self.BEARER_TOKEN,
            max_retries=5,
            backoff_factor=2.0
        )

        # Verify Retry class was instantiated with correct parameters
        mock_retry.assert_called_once_with(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=2.0,
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        # Verify HTTPAdapter was instantiated with the retry strategy
        mock_adapter.assert_called_once_with(max_retries=mock_retry.return_value)

        # Verify the adapter was mounted to the session for both http and https
        assert mock_session_instance.mount.call_count == 2
        mock_session_instance.mount.assert_any_call("https://", mock_adapter.return_value)
        mock_session_instance.mount.assert_any_call("http://", mock_adapter.return_value)

    @pytest.mark.parametrize("invalid_token", [None, "", 123])
    def test_constructor_with_invalid_token_raises_value_error(self, invalid_token):
        """
        Ensures the constructor raises a ValueError if the bearer_token is invalid.
        """
        with pytest.raises(ValueError, match="Bearer token cannot be null or empty."):
            TwitterClient(bearer_token=invalid_token)

    @pytest.mark.parametrize("invalid_ticker", ["TOOLONGTICKER", "B@DCHARS", ""])
    def test_search_tweets_with_invalid_ticker_raises_value_error(self, invalid_ticker):
        """
        Ensures search_tweets raises a ValueError for invalid ticker formats.
        """
        client = TwitterClient(bearer_token=self.BEARER_TOKEN)
        with pytest.raises(ValueError, match="Invalid ticker format."):
            client.search_tweets(invalid_ticker)

    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_success(self, mock_logging, mock_session):
        """
        Verifies the method returns a list of tweets on a 200 OK response.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.SUCCESS_PAYLOAD
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        client = TwitterClient(bearer_token=self.BEARER_TOKEN)
        # We need to manually set the session here because the fixture replaces it after init
        client.session = mock_session
        tweets = client.search_tweets(self.TICKER, max_tweets=2)

        assert tweets == self.SUCCESS_PAYLOAD["data"]
        mock_session.get.assert_called_once_with(
            client.BASE_URL,
            params={'query': self.QUERY, 'tweet.fields': client.DEFAULT_TWEET_FIELDS, 'max_results': 2},
            timeout=10
        )
        mock_logging.info.assert_called_with(f"Successfully fetched 2 tweets for ticker {self.TICKER}.")

    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_handles_http_error_after_retries(self, mock_logging, mock_session):
        """
        Verifies a non-retryable 4xx error is handled gracefully and logged correctly
        after the retry mechanism is exhausted.
        """
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = self.ERROR_PAYLOAD_400
        http_error = HTTPError(response=mock_response)
        mock_session.get.side_effect = http_error
        
        client = TwitterClient(bearer_token=self.BEARER_TOKEN)
        client.session = mock_session
        tweets = client.search_tweets(self.TICKER)

        mock_session.get.assert_called_once()
        mock_logging.error.assert_called_with(
            "HTTP error 400 for ticker AAPL after retries. Title: Invalid Request, Detail: Invalid 'query' parameter"
        )
        assert tweets == []

    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_handles_network_exception_after_retries(self, mock_logging, mock_session):
        """
        Verifies that a network exception is handled gracefully after all retries fail.
        """
        request_exception = RequestException("Connection timed out")
        mock_session.get.side_effect = request_exception

        client = TwitterClient(bearer_token=self.BEARER_TOKEN)
        client.session = mock_session
        tweets = client.search_tweets(self.TICKER)

        mock_session.get.assert_called_once()
        mock_logging.error.assert_called_with(
            f"Failed to fetch tweets for ticker {self.TICKER} after retries. Error: {request_exception}"
        )
        assert tweets == []
    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_with_pagination(self, mock_logging, mock_session):
        """
        Verifies that the client correctly handles paginated responses.
        """
        # First response with a next_token
        response1_payload = {
            "data": [{"id": "1", "text": "Tweet 1"}],
            "meta": {"result_count": 1, "next_token": "token123"}
        }
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = response1_payload
        mock_response1.raise_for_status.return_value = None

        # Second response without a next_token
        response2_payload = {
            "data": [{"id": "2", "text": "Tweet 2"}],
            "meta": {"result_count": 1}
        }
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = response2_payload
        mock_response2.raise_for_status.return_value = None

        mock_session.get.side_effect = [mock_response1, mock_response2]

        client = TwitterClient(bearer_token=self.BEARER_TOKEN)
        client.session = mock_session
        tweets = client.search_tweets(self.TICKER)

        assert mock_session.get.call_count == 2
        assert tweets == response1_payload["data"] + response2_payload["data"]
        
        # Check params for the second call
        second_call_args, second_call_kwargs = mock_session.get.call_args_list[1]
        assert second_call_kwargs['params']['pagination_token'] == 'token123'
        
        mock_logging.info.assert_any_call(f"Successfully fetched 1 tweets for ticker {self.TICKER}.")
        mock_logging.info.assert_any_call(f"Paginating... fetching next page for ticker {self.TICKER} with token token123.")


    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_respects_max_tweets(self, mock_logging, mock_session):
        """
        Ensures search_tweets stops fetching when max_tweets is reached.
        """
        response_payload = {
            "data": [
                {"id": "1", "text": "Tweet 1"},
                {"id": "2", "text": "Tweet 2"},
                {"id": "3", "text": "Tweet 3"},
            ],
            "meta": {"result_count": 3, "next_token": "token123"}
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_payload
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        client = TwitterClient(bearer_token=self.BEARER_TOKEN)
        client.session = mock_session
        tweets = client.search_tweets(self.TICKER, max_tweets=2)

        mock_session.get.assert_called_once()
        assert len(tweets) == 2
        assert tweets == response_payload["data"][:2]
        mock_logging.info.assert_called_with(f"Successfully fetched 2 tweets for ticker {self.TICKER}.")