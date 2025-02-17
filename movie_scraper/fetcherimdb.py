import os
import requests
import json
import time


#  Load API key from environment variable
API_KEY = os.getenv("dcc891360755426d4d6b137dce4c2896")  # Ensure you set this before running
if not API_KEY:
    raise ValueError("❌ ERROR: API key is missing! Set TMDB_API_KEY as an environment variable.")

# API base settings
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
MAX_REQUESTS_PER_SEC = 35  # Keeping below the 40/sec limit
SLEEP_TIME = 1.2  # To ensure we respect rate limits

# Get top 1000 rated movies
def fetch_top_movies():
    all_movies = []
    page = 1
    while len(all_movies) < 1000:
        print(f"📥 Fetching page {page} of movies...")
        url = f"{BASE_URL}/movie/top_rated?language=en-US&page={page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.json()}")
            break

        data = response.json()
        all_movies.extend(data["results"])

        if len(all_movies) >= 1000 or page >= data["total_pages"]:
            break

        page += 1
        time.sleep(SLEEP_TIME)  # Respecting API limits

    return all_movies[:1000]

#  Get reviews for a movie
def fetch_reviews(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/reviews?language=en-US&page=1"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"⚠️ No reviews for {movie_id}")
        return []

#  Fetch cast details for a movie
def fetch_cast(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        cast = response.json().get("cast", [])
        return [actor["name"] for actor in cast[:5]]  # Get top 5 actors
    else:
        print(f"⚠️ No cast details for {movie_id}")
        return []

#  Main function to fetch data and save it
def main():
    print("🎬 Fetching top 1000 movies...")
    movies = fetch_top_movies()

    movie_data = []
    for index, movie in enumerate(movies, start=1):
        print(f"🎥 Processing {index}/1000: {movie['title']} ({movie['id']})")
        movie_details = {
            "title": movie["title"],
            "id": movie["id"],
            "rating": movie["vote_average"],
            "vote_count": movie["vote_count"],
            "release_date": movie["release_date"],
            "genres": [genre["name"] for genre in movie["genre_ids"]],
            "overview": movie["overview"],
            "cast": fetch_cast(movie["id"]),
            "reviews": fetch_reviews(movie["id"])
        }
        movie_data.append(movie_details)

        if index % MAX_REQUESTS_PER_SEC == 0:
            print("⏳ Sleeping to respect API limits...")
            time.sleep(1)  # Small delay after a batch

    with open("tmdb_top1000.json", "w", encoding="utf-8") as f:
        json.dump(movie_data, f, indent=4)

    print("Data saved to tmdb_top1000.json")

#  Run script
if __name__ == "__main__":
    main()
