import time
import torch
from ml_sentiment import SentimentAnalysisModel

def profile_bulk_predict_sentiment(model, texts):
    """
    Profiles the bulk_predict_sentiment method.
    """
    start_time = time.time()
    results = model.bulk_predict_sentiment(texts)
    end_time = time.time()
    
    duration = end_time - start_time
    num_texts = len(texts)
    texts_per_second = num_texts / duration if duration > 0 else float('inf')
    
    print(f"Processed {num_texts} texts in {duration:.4f} seconds.")
    print(f"Throughput: {texts_per_second:.2f} texts/second.")
    return duration, texts_per_second

if __name__ == "__main__":
    print("Initializing model...")
    # Initialize the model
    sentiment_model = SentimentAnalysisModel()
    
    # Generate a list of sample texts for profiling
    sample_texts = [
        "The stock market is soaring to new heights, great news for investors.",
        "Analysts are predicting a downturn due to recent economic policies.",
        "The company's earnings report was neutral, meeting expectations but not exceeding them.",
        "Catastrophic losses are expected across the board.",
        "A surprising surge in tech stocks has everyone optimistic."
    ] * 200  # Create a batch of 1000 texts
    
    print(f"Starting profiling with {len(sample_texts)} texts...")
    
    # Warm-up run to load model onto GPU, etc.
    if sentiment_model.device == "cuda":
        print("Warming up the model...")
        sentiment_model.bulk_predict_sentiment(sample_texts[:10])

    # Profile the function
    profile_bulk_predict_sentiment(sentiment_model, sample_texts)