from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import streamlit as st

class MLSentimentAnalyzer:
    def __init__(self):
        # Use FinBERT model, specifically trained on financial texts
        model_name = "ProsusAI/finbert"
        
        # Cache the model loading using Streamlit
        @st.cache_resource
        def load_model():
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            return tokenizer, model
            
        self.tokenizer, self.model = load_model()
        self.labels = ['Negative', 'Neutral', 'Positive']
        
    def analyze_sentiment(self, text):
        if not text:
            return "Neutral", 0.0
            
        try:
            # Tokenize and prepare input
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # Get the predicted class and confidence
            predicted_class = torch.argmax(predictions).item()
            confidence = predictions[0][predicted_class].item()
            
            # Map to sentiment and normalize confidence to [-1, 1] for consistency
            sentiment = self.labels[predicted_class]
            if sentiment == "Positive":
                score = confidence
            elif sentiment == "Negative":
                score = -confidence
            else:
                score = 0.0
                
            return sentiment, score
            
        except Exception as e:
            st.error(f"ML Sentiment Analysis error: {str(e)}")
            return "Neutral", 0.0
            
    def get_sentiment_color(self, sentiment):
        colors = {
            "Positive": "#28a745",  # Green
            "Negative": "#dc3545",  # Red
            "Neutral": "#ffc107"    # Yellow
        }
        return colors.get(sentiment, "#ffc107")
