import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from langdetect import detect, DetectorFactory

# Ensure deterministic results for language detection
DetectorFactory.seed = 0

# Download necessary NLTK data files (if not already available)
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")

# Initialize NLTK tools
stop_words = set(stopwords.words("english")).union(
    {"movie", "film", "story", "great", "good", "best", "ever", "really"}
)
lemmatizer = WordNetLemmatizer()

# Function to check if a review is English
def is_english(text):
    try:
        # 🚀 Remove any non-English (non-ASCII) characters
        clean_text = re.sub(r"[^\x00-\x7F]+", "", text)  # Removes all non-ASCII characters

        # 🚀 If the cleaned text is empty, it's not English
        if not clean_text.strip():
            return False

        # 🚀 Detect language based on clean text
        return detect(clean_text) == "en"
    except:
        return False  # If detection fails, assume it's not English

# Function to clean a review (only if it's English)
def clean_review(text):
    if not text or not isinstance(text, str):  # Handle missing or invalid data
        return ""

    if not is_english(text):  # 🚨 Skip non-English reviews
        return ""

    text = text.lower().strip()  # Convert to lowercase & trim spaces
    text = re.sub(r"\d+", "", text)  # Remove numbers
    text = re.sub(r"http\S+|www\S+|<.*?>", "", text)  # Remove URLs & HTML tags
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces

    words = word_tokenize(text)  # Tokenize the text
    words = [word for word in words if word not in stop_words]  # Remove stopwords
    words = [lemmatizer.lemmatize(word) for word in words]  # Apply lemmatization

    return " ".join(words)  # Convert back to string

# Load the JSON file
input_file = "tmdb_movies500character.json"  # Make sure this file exists!
output_file = "tmdb_movies_cleaned_fixed.json"  # New output file

try:
    with open(input_file, "r", encoding="utf-8") as f:
        movies = json.load(f)
except FileNotFoundError:
    print(f"❌ Error: File '{input_file}' not found.")
    exit(1)
except json.JSONDecodeError:
    print("❌ Error: Invalid JSON format.")
    exit(1)

# Process each movie and clean reviews
for movie in movies:
    if "reviews" in movie and isinstance(movie["reviews"], list):
        movie["cleaned_reviews"] = [clean_review(review) for review in movie["reviews"]]

# Save the cleaned data to a new JSON file
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=4, ensure_ascii=False)
    print(f" Cleaned reviews saved to {output_file}")
except Exception as e:
    print(f"❌ Error: Could not save the cleaned JSON file: {e}")
