from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

class SentimentAnalyzer:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        self.sia = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, text):
        if not text:
            return "Neutral", 0.0

        scores = self.sia.polarity_scores(text)
        compound = float(scores['compound'])  # Ensure float type

        if compound >= 0.05:
            return "Positive", compound
        elif compound <= -0.05:
            return "Negative", compound
        else:
            return "Neutral", compound

    def get_sentiment_color(self, sentiment):
        colors = {
            "Positive": "#28a745",
            "Negative": "#dc3545",
            "Neutral": "#ffc107"
        }
        return colors.get(sentiment, "#ffc107")