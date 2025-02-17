import json
import nltk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download necessary data for sentiment analysis
nltk.download("vader_lexicon")

# Load the cleaned movie data
input_file = "tmdb_movies_cleaned_fixed.json"

try:
    with open(input_file, "r", encoding="utf-8") as f:
        movies = json.load(f)
except FileNotFoundError:
    print(f"❌ Error: File '{input_file}' not found.")
    exit(1)

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Store sentiment scores
for movie in movies:
    if "cleaned_reviews" in movie and movie["cleaned_reviews"]:
        sentiments = [sia.polarity_scores(review)["compound"] for review in movie["cleaned_reviews"]]
        movie["avg_sentiment"] = np.mean(sentiments) if sentiments else 0
    else:
        movie["avg_sentiment"] = 0

# Find most common words in reviews
all_words = []
for movie in movies:
    if "cleaned_reviews" in movie:
        all_words.extend(" ".join(movie["cleaned_reviews"]).split())

common_words = Counter(all_words).most_common(20)
print("\n🔹 Most Common Words in Reviews:", common_words)

# Visualize sentiment distribution
sentiment_scores = [movie["avg_sentiment"] for movie in movies]
plt.hist(sentiment_scores, bins=20, edgecolor="black")
plt.xlabel("Sentiment Score")
plt.ylabel("Number of Movies")
plt.title("Distribution of Sentiment Scores")
plt.show()

# Save the enriched data
output_file = "tmdb_movies_analyzed.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=4, ensure_ascii=False)

print(f" Analysis saved to {output_file}")
