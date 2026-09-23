"""
Sentiment Analysis Module
Uses NLTK VADER to analyze patient feedback.
"""

from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize VADER once (singleton pattern for speed)
_sia = None

def get_sia():
    """Get or create the SentimentIntensityAnalyzer instance."""
    global _sia
    if _sia is None:
        _sia = SentimentIntensityAnalyzer()
    return _sia


def analyze_sentiment(text):
    """
    Analyze sentiment of given text.
    
    Returns a dictionary:
    {
        'label': 'Positive' | 'Negative' | 'Neutral',
        'score': float (compound score between -1 and 1),
        'emoji': '😊' | '😞' | '😐',
        'color': 'success' | 'danger' | 'warning',
        'positive': float,
        'negative': float,
        'neutral': float
    }
    """
    if not text or not text.strip():
        return {
            'label': 'Neutral',
            'score': 0.0,
            'emoji': '😐',
            'color': 'warning',
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
        }
    
    sia = get_sia()
    scores = sia.polarity_scores(text)
    compound = scores['compound']
    
    # Classify based on compound score
    if compound >= 0.05:
        label = 'Positive'
        emoji = '😊'
        color = 'success'
    elif compound <= -0.05:
        label = 'Negative'
        emoji = '😞'
        color = 'danger'
    else:
        label = 'Neutral'
        emoji = '😐'
        color = 'warning'
    
    return {
        'label': label,
        'score': round(compound, 3),
        'emoji': emoji,
        'color': color,
        'positive': round(scores['pos'], 3),
        'negative': round(scores['neg'], 3),
        'neutral': round(scores['neu'], 3),
    }


def get_sentiment_stats(feedbacks):
    """
    Calculate overall sentiment statistics for a list of feedbacks.
    
    Args:
        feedbacks: iterable of objects with 'feedback_text' attribute
    
    Returns:
        {
            'positive': int,
            'negative': int,
            'neutral': int,
            'total': int,
            'positive_percent': float,
            'negative_percent': float,
            'neutral_percent': float,
            'average_score': float,
        }
    """
    positive = 0
    negative = 0
    neutral = 0
    total_score = 0
    total = 0
    
    for fb in feedbacks:
        text = getattr(fb, 'feedback_text', None) or ''
        result = analyze_sentiment(text)
        
        if result['label'] == 'Positive':
            positive += 1
        elif result['label'] == 'Negative':
            negative += 1
        else:
            neutral += 1
        
        total_score += result['score']
        total += 1
    
    if total == 0:
        return {
            'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0,
            'positive_percent': 0, 'negative_percent': 0, 'neutral_percent': 0,
            'average_score': 0,
        }
    
    return {
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
        'total': total,
        'positive_percent': round((positive / total) * 100, 1),
        'negative_percent': round((negative / total) * 100, 1),
        'neutral_percent': round((neutral / total) * 100, 1),
        'average_score': round(total_score / total, 3),
    }