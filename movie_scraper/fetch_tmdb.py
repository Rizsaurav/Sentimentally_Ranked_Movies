import requests
import time
import json

API_KEY = "dcc891360755426d4d6b137dce4c2896"
BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def fetch_movies(category="top_rated", max_movies=1000):
    movies = []
    page = 1
    while len(movies) < max_movies:
        print(f"🔄 Fetching {category} movies - Page {page}")
        response = requests.get(f"{BASE_URL}/movie/{category}", params={"api_key": API_KEY, "page": page}, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Error: {response.json()}")
            break

        data = response.json()
        movies.extend(data.get("results", []))

        if page >= data.get("total_pages", 1):
            break

        page += 1
        time.sleep(0.5)  #  Respect API limits

    return movies[:max_movies]

def fetch_movie_details(movie_id):
    response = requests.get(f"{BASE_URL}/movie/{movie_id}", params={"api_key": API_KEY}, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return {}

def fetch_movie_cast(movie_id):
    response = requests.get(f"{BASE_URL}/movie/{movie_id}/credits", params={"api_key": API_KEY}, headers=HEADERS)
    if response.status_code == 200:
        cast_data = response.json()
        cast = [member["name"] for member in cast_data.get("cast", [])[:5]]
        return cast
    return []

def fetch_movie_reviews(movie_id, max_reviews=100):  # Increased max_reviews
    reviews = []
    page = 1

    while len(reviews) < max_reviews:
        response = requests.get(
            f"{BASE_URL}/movie/{movie_id}/reviews",
            params={"api_key": API_KEY, "page": page},
            headers=HEADERS
        )

        if response.status_code != 200:
            break  # Stop if API call fails

        review_data = response.json()
        new_reviews = [review["content"][:500] for review in review_data.get("results", [])]

        if not new_reviews:
            break  # No more reviews available

        reviews.extend(new_reviews)

        if len(reviews) >= max_reviews or page >= review_data.get("total_pages", 1):
            break

        page += 1
        time.sleep(0.3)  #  Avoid hitting rate limits

    return reviews[:max_reviews]


def fetch_movie_director(movie_id):
    response = requests.get(f"{BASE_URL}/movie/{movie_id}/credits", params={"api_key": API_KEY}, headers=HEADERS)
    if response.status_code == 200:
        crew_data = response.json().get("crew", [])
        for member in crew_data:
            if member["job"] == "Director":
                return member["name"]
    return "N/A"

def fetch_movie_budget_revenue(movie_id):
    response = requests.get(f"{BASE_URL}/movie/{movie_id}", params={"api_key": API_KEY}, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return {
            "budget": data.get("budget", 0),
            "revenue": data.get("revenue", 0)
        }
    return {"budget": 0, "revenue": 0}

def save_json(data, filename="tmdb_movies.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f" Data saved to {filename}")

def main():
    all_movies = []
    movies = fetch_movies("top_rated", 500) + fetch_movies("popular", 500)

    for idx, movie in enumerate(movies):
        movie_id = movie["id"]
        print(f"🎬 Fetching details for: {movie['title']} ({idx+1}/{len(movies)})")

        details = fetch_movie_details(movie_id)
        cast = fetch_movie_cast(movie_id)
        reviews = fetch_movie_reviews(movie_id)
        director = fetch_movie_director(movie_id)
        budget_revenue = fetch_movie_budget_revenue(movie_id)

        movie_data = {
            "id": movie_id,
            "title": movie["title"],
            "year": movie["release_date"][:4] if "release_date" in movie else "N/A",
            "genres": [genre["name"] for genre in details.get("genres", [])],
            "rating": movie["vote_average"],
            "vote_count": movie["vote_count"],
            "runtime": details.get("runtime", "N/A"),
            "overview": movie.get("overview", ""),
            "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
            "cast": cast,
            "reviews": reviews,
            "director": director,
            "budget": f"${budget_revenue['budget']:,}" if budget_revenue["budget"] else "N/A",
            "revenue": f"${budget_revenue['revenue']:,}" if budget_revenue["revenue"] else "N/A"
        }

        all_movies.append(movie_data)

        if (idx + 1) % 20 == 0:
            print("⏳ Sleeping to respect API limits...")
            time.sleep(10)

    save_json(all_movies, "tmdb_movies500character.json")

if __name__ == "__main__":
    main()
