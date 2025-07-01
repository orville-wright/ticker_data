import unittest
from unittest.mock import patch, Mock, call
import logging
import time

# This import will fail, which is expected in TDD.
# The coder will create this module and class.
from data_ingestion.alpha_vantage_client import AlphaVantageClient

# Suppress logging output during tests
logging.basicConfig(level=logging.CRITICAL)

class TestAlphaVantageClient(unittest.TestCase):

    def setUp(self):
        """Set up common test data."""
        self.api_key = "TEST_KEY"
        self.symbol = "TEST"
        self.base_url = "https://www.alphavantage.co/query"
        self.success_response = {
            "Meta Data": {"2. Symbol": "TEST"},
            "Time Series (Daily)": {
                "2025-06-30": {"1. open": "100.00"},
                "2025-06-29": {"1. open": "99.00"}
            }
        }
        self.error_response = {}

    @patch('data_ingestion.alpha_vantage_client.requests.Session.get')
    def test_fetch_daily_time_series_success(self, mock_get):
        """
        TC-AVC-001: Verifies successful data fetch.
        Tests that the client correctly fetches and returns time-series data
        when the API returns a 200 OK status.
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.success_response
        mock_get.return_value = mock_response

        client = AlphaVantageClient(api_key=self.api_key)

        # Act
        data = client.fetch_daily_time_series(self.symbol)

        # Assert
        expected_params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': self.symbol,
            'outputsize': 'compact',
            'apikey': self.api_key
        }
        mock_get.assert_called_once_with(self.base_url, params=expected_params, timeout=client.timeout)
        self.assertEqual(data, self.success_response)

    @patch('data_ingestion.alpha_vantage_client.logging.error')
    @patch('data_ingestion.alpha_vantage_client.requests.Session.get')
    def test_fetch_daily_time_series_api_error(self, mock_get, mock_log_error):
        """
        TC-AVC-002: Verifies API error handling.
        Tests that the client returns an empty dictionary and logs an error
        when the API returns a non-200 status code.
        """
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_get.return_value = mock_response

        client = AlphaVantageClient(api_key=self.api_key)

        # Act
        data = client.fetch_daily_time_series(self.symbol)

        # Assert
        expected_params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': self.symbol,
            'outputsize': 'compact',
            'apikey': self.api_key
        }
        mock_get.assert_called_once_with(self.base_url, params=expected_params, timeout=client.timeout)
        mock_log_error.assert_called()
        self.assertEqual(data, {})

    @patch('data_ingestion.alpha_vantage_client.time.sleep')
    @patch('data_ingestion.alpha_vantage_client.requests.Session.get')
    def test_fetch_daily_time_series_rate_limit_with_backoff(self, mock_get, mock_sleep):
        """
        TC-AVC-003: Verifies rate limit handling with exponential backoff.
        Tests that the client retries with a delay upon receiving a 429 status,
        and eventually succeeds.
        """
        # Arrange
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.reason = "Too Many Requests"

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = self.success_response

        # requests.get will first return a 429, then a 200
        mock_get.side_effect = [mock_response_429, mock_response_200]

        client = AlphaVantageClient(api_key=self.api_key, max_retries=2)

        # Act
        data = client.fetch_daily_time_series(self.symbol)

        # Assert
        expected_params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': self.symbol,
            'outputsize': 'compact',
            'apikey': self.api_key
        }
        # Assert it was called twice
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_has_calls([
            call(self.base_url, params=expected_params, timeout=client.timeout),
            call(self.base_url, params=expected_params, timeout=client.timeout)
        ])

        # Assert that sleep was called once with the initial backoff delay
        mock_sleep.assert_called_once_with(1)

        # Assert that the final result is the successful response
        self.assertEqual(data, self.success_response)

    @patch('data_ingestion.alpha_vantage_client.logging.error')
    def test_fetch_daily_time_series_invalid_symbol(self, mock_log_error):
        """
        TC-AVC-004: Verifies behavior with an invalid symbol format.
        """
        # Arrange
        client = AlphaVantageClient(api_key=self.api_key)
        invalid_symbol = "INVALID$SYMBOL"

        # Act
        data = client.fetch_daily_time_series(invalid_symbol)

        # Assert
        mock_log_error.assert_called_with(f"Invalid symbol format provided: {invalid_symbol}")
        self.assertEqual(data, {})

    def test_init_with_timeout(self):
        """
        TC-AVC-005: Verifies that the timeout is correctly set during initialization.
        """
        # Arrange
        client = AlphaVantageClient(api_key=self.api_key, timeout=60)

        # Assert
        self.assertEqual(client.timeout, 60)

if __name__ == '__main__':
    unittest.main()