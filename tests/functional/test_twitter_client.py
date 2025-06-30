import pytest
from unittest.mock import patch, MagicMock, call
from requests.exceptions import Timeout

# This import will fail initially, which is expected in TDD
from data_ingestion.twitter_client import TwitterClient

class TestTwitterClient:
    """
    Test suite for the TwitterClient class, following the London School of TDD.
    """

    BEARER_TOKEN = "test_bearer_token"
    BASE_URL = "https://api.twitter.com/2/tweets/search/recent"
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
    def client(self):
        """Provides a TwitterClient instance for testing."""
        return TwitterClient(bearer_token=self.BEARER_TOKEN)

    # Test Case ID: TC1_INIT_SUCCESS
    def test_constructor_assigns_properties_correctly(self):
        """
        Verifies that the constructor correctly assigns the bearer_token
        and sets the default base_url.
        """
        client = TwitterClient(bearer_token=self.BEARER_TOKEN)
        assert client.bearer_token == self.BEARER_TOKEN
        assert client.base_url == self.BASE_URL

    # Test Case ID: TC2_INIT_INVALID_TOKEN
    @pytest.mark.parametrize("invalid_token", [None, "", 123])
    def test_constructor_with_invalid_token_raises_value_error(self, invalid_token):
        """
        Ensures the constructor raises a ValueError if the bearer_token is invalid.
        """
        with pytest.raises(ValueError):
            TwitterClient(bearer_token=invalid_token)

    # Test Case ID: TC3_SEARCH_SUCCESS
    @patch('data_ingestion.twitter_client.requests.get')
    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_success(self, mock_logging, mock_get, client):
        """
        Verifies that the method returns a list of tweet dictionaries on a 200 OK response.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.SUCCESS_PAYLOAD
        mock_get.return_value = mock_response

        tweets = client.search_tweets(self.TICKER)

        assert tweets == self.SUCCESS_PAYLOAD["data"]
        assert len(tweets) == 2
        mock_get.assert_called_once_with(
            client.base_url,
            headers={"Authorization": f"Bearer {self.BEARER_TOKEN}"},
            params={'query': self.QUERY, 'tweet.fields': 'created_at,public_metrics,lang'}
        )
        mock_logging.info.assert_called_with(f"Successfully fetched {self.SUCCESS_PAYLOAD['meta']['result_count']} tweets for ticker ${self.TICKER}.")

    # Test Case ID: TC4_SEARCH_RATE_LIMIT
    @patch('data_ingestion.twitter_client.time.sleep')
    @patch('data_ingestion.twitter_client.requests.get')
    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_rate_limit_with_backoff(self, mock_logging, mock_get, mock_sleep, client):
        """
        Verifies that the method handles a 429 error by retrying with exponential backoff.
        """
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = self.SUCCESS_PAYLOAD
        
        mock_get.side_effect = [mock_response_429, mock_response_200]

        tweets = client.search_tweets(self.TICKER)

        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(1)
        mock_logging.warning.assert_called_with(f"Rate limit exceeded for ticker ${self.TICKER}. Retrying in 1 seconds...")
        assert tweets == self.SUCCESS_PAYLOAD["data"]

    # Test Case ID: TC5_SEARCH_RETRY_FAILURE
    @patch('data_ingestion.twitter_client.time.sleep')
    @patch('data_ingestion.twitter_client.requests.get')
    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_failure_after_all_retries(self, mock_logging, mock_get, mock_sleep, client):
        """
        Verifies that the method returns an empty list after exhausting all retry attempts.
        """
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_get.return_value = mock_response_429

        # Assuming MAX_RETRIES = 3
        expected_sleeps = [call(1), call(2)]

        tweets = client.search_tweets(self.TICKER)

        assert mock_get.call_count == 3
        mock_sleep.assert_has_calls(expected_sleeps)
        mock_logging.error.assert_called_with(f"Failed to fetch tweets for ticker ${self.TICKER} after 3 retries.")
        assert tweets == []

    # Test Case ID: TC6_SEARCH_HTTP_ERROR
    @patch('data_ingestion.twitter_client.requests.get')
    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_handles_other_http_error(self, mock_logging, mock_get, client):
        """
        Verifies that a non-429 HTTP error is handled gracefully without retrying.
        """
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = self.ERROR_PAYLOAD_400
        mock_get.return_value = mock_response

        tweets = client.search_tweets(self.TICKER)

        mock_get.assert_called_once()
        mock_logging.error.assert_called_with(
            f"HTTP error 400 for ticker ${self.TICKER}: {self.ERROR_PAYLOAD_400}"
        )
        assert tweets == []

    # Test Case ID: TC7_SEARCH_NETWORK_ERROR
    @patch('data_ingestion.twitter_client.time.sleep')
    @patch('data_ingestion.twitter_client.requests.get')
    @patch('data_ingestion.twitter_client.logging')
    def test_search_tweets_handles_network_exception(self, mock_logging, mock_get, mock_sleep, client):
        """
        Verifies that a network exception is handled with a retry.
        """
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = self.SUCCESS_PAYLOAD

        mock_get.side_effect = [Timeout("Connection timed out"), mock_response_200]

        tweets = client.search_tweets(self.TICKER)

        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(1)
        mock_logging.error.assert_called_with(f"Network error for ticker ${self.TICKER}: Connection timed out. Retrying in 1 seconds...")
        assert tweets == self.SUCCESS_PAYLOAD["data"]