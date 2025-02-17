import json
import torch
from transformers import pipeline

# Load pre-trained sentiment model from Hugging Face
sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Load JSON File
input_file = "tmdb_movies_cleaned_fixed.json"

with open(input_file, "r", encoding="utf-8") as f:
    movies = json.load(f)

# Function to get sentiment score from DistilBERT
def get_sentiment(text):
    if not text:
        return 0  # Neutral if empty
    result = sentiment_model(text[:512])  # DistilBERT has a 512-token limit
    score = result[0]['score']
    return score if result[0]['label'] == "POSITIVE" else -score

# Process each movie and analyze sentiment
for movie in movies:
    reviews = movie.get("cleaned_reviews", [])
    sentiment_scores = [get_sentiment(review) for review in reviews]
    
    # Compute average sentiment score for the movie
    movie["sentiment_score"] = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

# Save updated JSON with sentiment scores
output_file = "tmdb_movies_sentiment.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=4, ensure_ascii=False)

print(f" Sentiment analysis completed! Data saved to {output_file}")
