import unittest
from unittest.mock import MagicMock, patch

from data_ingestion.pipeline import run_ingestion_pipeline
from data_ingestion.alpha_vantage_client import AlphaVantageClient
from data_ingestion.twitter_client import TwitterClient

class TestIngestionPipeline(unittest.TestCase):

    def setUp(self):
        """Set up mock clients and sample data for tests."""
        # Create mock instances of the clients
        self.mock_alpha_vantage_client = MagicMock(spec=AlphaVantageClient)
        self.mock_twitter_client = MagicMock(spec=TwitterClient)

        # Sample data for successful API calls
        self.sample_price_data = {"Time Series (Daily)": {"2023-01-01": {"1. open": "150.00"}}}
        self.sample_tweet_data = [{"id": "123", "text": "This is a tweet about AAPL"}]

    def test_run_ingestion_pipeline_happy_path(self):
        """
        Tests the pipeline with successful data fetching for all stocks.
        Verifies AI Actionable End Result: Successful aggregation of data from all sources.
        """
        # Configure mocks to return successful data for both stocks
        self.mock_alpha_vantage_client.fetch_daily_time_series.return_value = self.sample_price_data
        self.mock_twitter_client.search_tweets.return_value = self.sample_tweet_data

        stocks_to_fetch = ["AAPL", "GOOG"]

        # Action: Run the pipeline
        ingested_data = run_ingestion_pipeline(
            stocks=stocks_to_fetch,
            alpha_vantage_client=self.mock_alpha_vantage_client,
            twitter_client=self.mock_twitter_client
        )

        # Assertions
        self.assertIn("AAPL", ingested_data)
        self.assertIn("GOOG", ingested_data)
        self.assertEqual(ingested_data["AAPL"]["price_data"], self.sample_price_data)
        self.assertEqual(ingested_data["AAPL"]["tweet_data"], self.sample_tweet_data)
        self.assertEqual(ingested_data["GOOG"]["price_data"], self.sample_price_data)
        self.assertEqual(ingested_data["GOOG"]["tweet_data"], self.sample_tweet_data)

        # Verify mocks were called for each stock
        self.assertEqual(self.mock_alpha_vantage_client.fetch_daily_time_series.call_count, 2)
        self.assertEqual(self.mock_twitter_client.search_tweets.call_count, 2)

    def test_run_ingestion_pipeline_with_partial_failures(self):
        """
        Tests the pipeline's resilience when one of the clients fails for one stock.
        Verifies AI Actionable End Result: Pipeline continues processing and returns structured
        output with empty data for the failed stock, avoiding bad fallbacks.
        """
        # Configure the Alpha Vantage mock to raise an exception for one stock
        def av_side_effect(symbol):
            if symbol == "FAIL":
                raise ValueError("Simulated API Error from Alpha Vantage")
            return self.sample_price_data

        self.mock_alpha_vantage_client.fetch_daily_time_series.side_effect = av_side_effect
        # The Twitter client can succeed for all calls in this scenario
        self.mock_twitter_client.search_tweets.return_value = self.sample_tweet_data

        stocks_to_fetch = ["AAPL", "FAIL"]

        # Action: Run the pipeline
        ingested_data = run_ingestion_pipeline(
            stocks=stocks_to_fetch,
            alpha_vantage_client=self.mock_alpha_vantage_client,
            twitter_client=self.mock_twitter_client
        )

        # Assertions for the successful stock ("AAPL")
        self.assertIn("AAPL", ingested_data)
        self.assertEqual(ingested_data["AAPL"]["price_data"], self.sample_price_data)
        self.assertEqual(ingested_data["AAPL"]["tweet_data"], self.sample_tweet_data)

        # Assertions for the failed stock ("FAIL")
        self.assertIn("FAIL", ingested_data)
        self.assertEqual(ingested_data["FAIL"]["price_data"], {})
        self.assertEqual(ingested_data["FAIL"]["tweet_data"], [])

        # Verify mock call counts
        # Alpha Vantage is attempted for both stocks
        self.assertEqual(self.mock_alpha_vantage_client.fetch_daily_time_series.call_count, 2)
        # Twitter is only called for the successful stock ("AAPL") due to the exception
        self.assertEqual(self.mock_twitter_client.search_tweets.call_count, 1)

if __name__ == '__main__':
    unittest.main()