"""
This module contains the implementation for the sentiment analysis model
and related utility functions.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SentimentAnalysisModel:
    """
    A class to encapsulate the sentiment analysis model.
    """
    def __init__(self, model_name: str = 'ProsusAI/finbert'):
        """
        Initializes and loads the sentiment analysis model and tokenizer.
        """
        if model_name != 'ProsusAI/finbert':
            raise ValueError("Only 'ProsusAI/finbert' model is allowed.")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)

    def predict_sentiment(self, text: str) -> dict:
        """
        Predicts the sentiment of a single text string.
        """
        tokens = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        tokens = {key: val.to(self.device) for key, val in tokens.items()}

        with torch.no_grad():
            outputs = self.model(**tokens)
            logits = outputs.logits

        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        prediction_idx = torch.argmax(probabilities, dim=-1).item()
        
        score = probabilities[0, prediction_idx].item()
        label = self.model.config.id2label[prediction_idx]

        return {'label': label, 'score': score}

    def bulk_predict_sentiment(self, texts: list[str]) -> list[dict]:
        """
        Predicts the sentiment for a list of text strings.
        """
        if len(texts) > 1000:
            raise ValueError("Cannot process more than 1000 texts at a time.")
        tokens = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        tokens = {key: val.to(self.device) for key, val in tokens.items()}

        with torch.no_grad():
            outputs = self.model(**tokens)
            logits = outputs.logits

        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        prediction_indices = torch.argmax(probabilities, dim=-1)

        scores = probabilities.gather(1, prediction_indices.unsqueeze(1)).squeeze().tolist()
        labels = [self.model.config.id2label[idx.item()] for idx in prediction_indices]

        return [{'label': label, 'score': score} for label, score in zip(labels, scores)]


def aggregate_daily_sentiment(predictions: list[dict]) -> dict:
    """
    Aggregates a list of sentiment predictions into a single daily score.
    """
    if not predictions:
        return {
            'daily_sentiment_score': 0.0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0
        }

    label_to_value = {'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0}
    
    total_weighted_score = 0.0
    total_weight = 0.0
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for pred in predictions:
        label = pred['label']
        score = pred['score']
        
        if label == 'POSITIVE':
            positive_count += 1
        elif label == 'NEGATIVE':
            negative_count += 1
        elif label == 'NEUTRAL':
            neutral_count += 1
            
        numeric_value = label_to_value.get(label, 0)
        total_weighted_score += numeric_value * score
        total_weight += score

    daily_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

    return {
        'daily_sentiment_score': daily_score,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
    }
