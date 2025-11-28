"""
Sentiment Agent for ARION
Analyzes news sentiment using VADER
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentAgent:
    """Analyzes market sentiment from news headlines"""
    
    def __init__(self):
        """Initialize Sentiment Agent"""
        self.analyzer = SentimentIntensityAnalyzer()
        self.last_analysis = {}
        
    def analyze(self, news_data: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze sentiment from news data
        
        Args:
            news_data: Dictionary mapping symbols to list of news articles
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        if not news_data:
            return self._empty_result()
        
        sentiment_scores = {}
        sentiment_labels = {}
        article_counts = {}
        
        for symbol, articles in news_data.items():
            if not articles:
                continue
            
            scores = []
            
            for article in articles:
                title = article.get('title', '')
                if not title:
                    continue
                
                # Analyze sentiment
                sentiment = self.analyzer.polarity_scores(title)
                scores.append(sentiment['compound'])
            
            if scores:
                avg_score = np.mean(scores)
                sentiment_scores[symbol] = avg_score
                sentiment_labels[symbol] = self._get_sentiment_label(avg_score)
                article_counts[symbol] = len(scores)
            else:
                sentiment_scores[symbol] = 0
                sentiment_labels[symbol] = 'NEUTRAL'
                article_counts[symbol] = 0
        
        # Calculate overall market sentiment
        if sentiment_scores:
            overall_score = np.mean(list(sentiment_scores.values()))
            overall_label = self._get_sentiment_label(overall_score)
            
            # Count sentiment distribution
            positive_count = sum(1 for label in sentiment_labels.values() if label == 'POSITIVE')
            negative_count = sum(1 for label in sentiment_labels.values() if label == 'NEGATIVE')
            neutral_count = sum(1 for label in sentiment_labels.values() if label == 'NEUTRAL')
        else:
            overall_score = 0
            overall_label = 'NEUTRAL'
            positive_count = 0
            negative_count = 0
            neutral_count = 0
        
        # Generate alerts for extreme sentiment
        alerts = []
        for symbol, score in sentiment_scores.items():
            if score < -0.5:
                alerts.append({
                    'symbol': symbol,
                    'type': 'NEGATIVE_SENTIMENT',
                    'severity': 'HIGH' if score < -0.7 else 'MEDIUM',
                    'message': f'{symbol}: Strong negative sentiment detected ({score:.2f})',
                    'value': score
                })
            elif score > 0.5:
                alerts.append({
                    'symbol': symbol,
                    'type': 'POSITIVE_SENTIMENT',
                    'severity': 'LOW',
                    'message': f'{symbol}: Strong positive sentiment detected ({score:.2f})',
                    'value': score
                })
        
        self.last_analysis = {
            'overall_score': overall_score,
            'overall_label': overall_label,
            'individual_scores': sentiment_scores,
            'individual_labels': sentiment_labels,
            'article_counts': article_counts,
            'distribution': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            },
            'alerts': alerts,
            'confidence': self._calculate_confidence(article_counts)
        }
        
        return self.last_analysis
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.2:
            return 'POSITIVE'
        elif score < -0.2:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
    
    def _calculate_confidence(self, article_counts: Dict[str, int]) -> float:
        """Calculate confidence based on number of articles analyzed"""
        if not article_counts:
            return 0.0
        
        # More articles = higher confidence
        avg_articles = np.mean(list(article_counts.values()))
        
        # Confidence scales with article count (max at 10+ articles)
        confidence = min(1.0, avg_articles / 10)
        
        return confidence
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'overall_score': 0,
            'overall_label': 'NEUTRAL',
            'individual_scores': {},
            'individual_labels': {},
            'article_counts': {},
            'distribution': {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            },
            'alerts': [],
            'confidence': 0.0
        }
    
    def return_signal(self) -> str:
        """Return simple signal based on last analysis"""
        if not self.last_analysis:
            return "NO_DATA"
        
        label = self.last_analysis.get('overall_label', 'NEUTRAL')
        score = self.last_analysis.get('overall_score', 0)
        
        if label == 'NEGATIVE':
            if score < -0.5:
                return "VERY_NEGATIVE"
            else:
                return "NEGATIVE"
        elif label == 'POSITIVE':
            if score > 0.5:
                return "VERY_POSITIVE"
            else:
                return "POSITIVE"
        else:
            return "NEUTRAL"
    
    def return_confidence(self) -> float:
        """Return confidence in last analysis"""
        return self.last_analysis.get('confidence', 0.0)


if __name__ == "__main__":
    # Test the sentiment agent
    import sys
    sys.path.append('..')
    from utils.fetch_data import DataFetcher
    
    fetcher = DataFetcher()
    news = fetcher.fetch_news(['AAPL', 'TSLA', 'NVDA'])
    
    agent = SentimentAgent()
    result = agent.analyze(news)
    
    print("Sentiment Analysis Results:")
    print(f"Overall Sentiment: {result['overall_label']} ({result['overall_score']:.2f})")
    print(f"Signal: {agent.return_signal()}")
    print(f"Confidence: {agent.return_confidence():.2%}")
    print("\nIndividual Sentiments:")
    for symbol, label in result['individual_labels'].items():
        score = result['individual_scores'][symbol]
        count = result['article_counts'][symbol]
        print(f"  {symbol}: {label} ({score:.2f}) - {count} articles")
    print(f"\nAlerts: {len(result['alerts'])}")
    for alert in result['alerts']:
        print(f"  - {alert['message']}")
