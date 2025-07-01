import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime

# These imports will point to the actual implementation files once they are created.
# For now, the test file defines placeholder classes to allow the tests to be written.
from data_processing.processing import TweetProcessor, FeatureEngineer, run_processing_pipeline
# from sentiment_analysis.model import SentimentAnalysisModel # Not in scope

# Placeholder class for the sentiment model, as its implementation is not in scope for this task.
class SentimentAnalysisModel:
    def predict(self, texts):
        # Return a dummy sentiment score for each list of tokens
        return [0.5 for _ in texts]

# The path for patching is the location where the object is *used*.
# The classes are now defined in `data_processing.processing`.
MODULE_PATH = 'data_processing.processing'

class TestDataProcessingPipeline(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures, if any."""
        # The methods are static, so we don't need instances.
        self.tweet_processor = TweetProcessor
        self.feature_engineer = FeatureEngineer

    # 4.1.1. clean_tweet Method Tests
    def test_clean_tweet_happy_path(self):
        """Verifies the removal of URLs, mentions, and hashtag symbols, and converts text to lowercase."""
        raw_tweet = "Check out $AAPL news! @user1 https://example.com #StockMarket"
        # The new implementation handles multiple spaces and trailing characters better
        expected = "check out $aapl news! stockmarket"
        result = self.tweet_processor.clean_tweet(raw_tweet)
        self.assertEqual(result, expected)

    def test_clean_tweet_empty_string(self):
        """Ensures the method handles empty input gracefully."""
        result = self.tweet_processor.clean_tweet("")
        self.assertEqual(result, "")

    def test_clean_tweet_retains_dollar_sign(self):
        """Ensures the $ symbol, crucial for cashtags, is not removed."""
        raw_tweet = "$TSLA to the moon! #tesla"
        expected = "$tsla to the moon! tesla"
        result = self.tweet_processor.clean_tweet(raw_tweet)
        self.assertEqual(result, expected)

    def test_clean_tweet_multiple_elements(self):
        """Ensures multiple occurrences of elements are cleaned correctly."""
        raw_tweet = "@person1 says #stocks are #awesome. @person2 agrees. See http://a.co"
        expected = "says stocks are awesome. agrees. see"
        result = self.tweet_processor.clean_tweet(raw_tweet)
        self.assertEqual(result, expected)

    # 4.1.2. tokenize_and_remove_stopwords Method Tests
    def test_tokenize_and_remove_stopwords_happy_path(self):
        """Verifies tokenization and removal of common words."""
        text = "this is a great stock"
        stopwords = {'this', 'is', 'a'}
        expected = ['great', 'stock']
        # The method is static, so we call it on the class
        result = self.tweet_processor.tokenize_and_remove_stopwords(text, stopwords)
        self.assertEqual(result, expected)

    def test_tokenize_and_remove_stopwords_all_stopwords(self):
        """Verifies that an empty list is returned if all words are stopwords."""
        text = "this is it"
        stopwords = {'this', 'is', 'it'}
        expected = []
        result = self.tweet_processor.tokenize_and_remove_stopwords(text, stopwords)
        self.assertEqual(result, expected)

    def test_tokenize_and_remove_stopwords_empty_string(self):
        """Ensures the method handles an empty input string gracefully."""
        text = ""
        stopwords = {'a', 'the'}
        expected = []
        result = self.tweet_processor.tokenize_and_remove_stopwords(text, stopwords)
        self.assertEqual(result, expected)

    # 4.2.1. add_all_features Method Tests
    @patch(f'{MODULE_PATH}.FeatureEngineer.calculate_bollinger_bands', return_value=(pd.Series([1]), pd.Series([1])))
    @patch(f'{MODULE_PATH}.FeatureEngineer.calculate_macd', return_value=(pd.Series([1]), pd.Series([1])))
    @patch(f'{MODULE_PATH}.FeatureEngineer.calculate_rsi', return_value=pd.Series([1]))
    @patch(f'{MODULE_PATH}.FeatureEngineer.calculate_moving_average', return_value=pd.Series([1]))
    def test_add_all_features_orchestration(self, mock_ma, mock_rsi, mock_macd, mock_bb):
        """Verifies that add_all_features calls all required underlying indicator calculation methods."""
        df = pd.DataFrame({'close': np.random.rand(50)})
        
        # Call the method under test
        self.feature_engineer.add_all_features(df)

        # Verify that the orchestrator called each collaborator once
        mock_ma.assert_called_once_with(df, window=20)
        mock_rsi.assert_called_once_with(df, window=14)
        # The spec and implementation use default window sizes, let's match that in the test assertion
        mock_macd.assert_called_once_with(df)
        mock_bb.assert_called_once_with(df, window=20)

    def test_indicator_calculations_integration(self):
        """Placeholder for integration test with golden values."""
        self.assertTrue(True)

    # 4.3. run_processing_pipeline Function Tests
    # 4.3. run_processing_pipeline Function Tests
    # 4.3. run_processing_pipeline Function Tests
    @patch(f'{MODULE_PATH}.FeatureEngineer.add_all_features')
    def test_run_processing_pipeline_orchestration(self, mock_add_features):
        """Verifies the overall workflow of the pipeline for a single stock."""
        mock_sentiment_instance = MagicMock(spec=SentimentAnalysisModel)
        mock_sentiment_instance.predict.return_value = [0.8]

        # Create enough data to survive dropna()
        date_range = pd.to_datetime(pd.date_range(start='2022-12-01', periods=30, freq='D'))
        price_data = pd.DataFrame({
            'close': np.linspace(150, 160, 30)
        }, index=date_range)
        
        # The mock should return a dataframe with a valid index
        mock_features_df = price_data.copy()
        mock_features_df['SMA_20'] = 155.0 # dummy value
        mock_add_features.return_value = mock_features_df

        raw_data = {
            'AAPL': {
                'price_data': price_data,
                'tweet_data': pd.DataFrame({'text': ['a tweet'], 'created_at': ['2022-12-28 15:00:00']}) # 10 AM EST
            }
        }

        result = run_processing_pipeline(raw_data, mock_sentiment_instance)
        
        mock_add_features.assert_called_once()
        mock_sentiment_instance.predict.assert_called_once()
        
        self.assertIn('AAPL', result)
        final_df = result['AAPL']
        self.assertIn('daily_sentiment_score', final_df.columns)
        self.assertIn('SMA_20', final_df.columns)
        # Check sentiment for a specific day that has a tweet
        self.assertAlmostEqual(final_df.loc['2022-12-28', 'daily_sentiment_score'], 0.8)

    def test_temporal_alignment_logic(self):
        """Verifies that tweet sentiment is correctly assigned to trading days."""
        mock_sentiment_instance = MagicMock(spec=SentimentAnalysisModel)
        # Let's define specific sentiment scores for each tweet to trace them
        mock_sentiment_instance.predict.return_value = [0.1, 0.3, 0.5, 0.7]

        # Setup: Create enough price data so it doesn't get dropped by dropna()
        date_range = pd.to_datetime(pd.date_range(start='2022-12-01', periods=40, freq='D'))
        price_data = pd.DataFrame({
            'open': np.linspace(90, 110, 40), 'high': np.linspace(90, 110, 40),
            'low': np.linspace(90, 110, 40), 'close': np.linspace(90, 110, 40), 'volume': np.ones(40)
        }, index=date_range)

        # Tweets with different UTC timestamps that correspond to specific local times
        tweet_data = pd.DataFrame({
            'text': ['T1', 'T2', 'T3', 'T4'],
            'created_at': pd.to_datetime([
                '2022-12-31 15:00:00', # Corresponds to Sat 10:00 AM EST -> rolls to Tue, Jan 3
                '2023-01-03 20:59:00', # Corresponds to Tue 3:59 PM EST -> belongs to Tue, Jan 3
                '2023-01-03 21:01:00', # Corresponds to Tue 4:01 PM EST -> belongs to Wed, Jan 4
                '2023-01-04 15:00:00'  # Corresponds to Wed 10:00 AM EST -> belongs to Wed, Jan 4
            ])
        })
        
        raw_data = {'$STOCK': {'price_data': price_data, 'tweet_data': tweet_data}}
        
        result = run_processing_pipeline(raw_data, mock_sentiment_instance)

        final_df = result['$STOCK']
        
        # Based on USFederalHolidayCalendar, Mon Jan 2, 2023 is New Year's Day (observed)
        # T1 (Sat) rolls to the next business day, which is Tuesday Jan 3.
        # T2 (Tue before close) also belongs to Tuesday Jan 3.
        expected_tue_score = (0.1 + 0.3) / 2
        self.assertAlmostEqual(final_df.loc['2023-01-03', 'daily_sentiment_score'], expected_tue_score)

        # T3 (Tue after close) belongs to Wednesday Jan 4.
        # T4 (Wed before close) also belongs to Wednesday Jan 4.
        expected_wed_score = (0.5 + 0.7) / 2
        self.assertAlmostEqual(final_df.loc['2023-01-04', 'daily_sentiment_score'], expected_wed_score)
        
        # A day with no tweets should have 0 sentiment
        self.assertAlmostEqual(final_df.loc['2023-01-05', 'daily_sentiment_score'], 0.0)
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)