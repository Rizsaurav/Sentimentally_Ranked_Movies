from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient
import json

#  Initialize FastAPI before defining any routes
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this later for security)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  PostgreSQL Configuration
POSTGRES_DB_URL = "postgresql://saurav@localhost/movies_db"

#  MongoDB Configuration
MONGO_DB_URL = "mongodb://localhost:27017/"
MONGO_DB_NAME = "movies_db"

#  Path to JSON file
JSON_FILE = "tmdb_movies_sentiment.json"

def connect_postgres():
    """Connect to PostgreSQL and create tables if not exist."""
    try:
        conn = psycopg2.connect(POSTGRES_DB_URL)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id SERIAL PRIMARY KEY,
                title TEXT UNIQUE,
                genre TEXT[],       
                rating FLOAT,
                sentiment_score FLOAT,
                actors TEXT[]       
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_search_history (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                search_query TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print(" Connected to PostgreSQL and ensured tables exist.")
        return conn, cursor
    except Exception as e:
        print(f"❌ PostgreSQL connection error: {e}")
        return None, None

def connect_mongo():
    """Connect to MongoDB and return the movies collection."""
    try:
        client = MongoClient(MONGO_DB_URL)
        db = client[MONGO_DB_NAME]
        print("Connected to MongoDB.")
        return db["movies"]
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return None

#  Initialize Databases
postgres_conn, postgres_cursor = connect_postgres()
mongo_collection = connect_mongo()

def load_movies_from_json():
    """Load movies from JSON and insert them into PostgreSQL."""
    if not postgres_conn or not postgres_cursor:
        print("❌ Database connection failed")
        return

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            movies = json.load(f)

        movie_data = [
            (
                movie["title"],
                movie["genres"],
                movie.get("rating", None),
                movie.get("sentiment_score", 0.0),
                movie.get("cast", [])
            )
            for movie in movies
        ]

        execute_values(postgres_cursor, """
            INSERT INTO movies (title, genre, rating, sentiment_score, actors)
            VALUES %s
            ON CONFLICT (title) DO NOTHING;
        """, movie_data)

        postgres_conn.commit()
        print("Movies loaded successfully into PostgreSQL.")

    except Exception as e:
        print(f"❌ Error loading movies: {e}")

#  Load JSON Data When API Starts
load_movies_from_json()

@app.get("/")
def home():
    return {"message": "🎬 Movie Recommender API is running!"}


@app.get("/search")
def search_movies(q: str = Query(..., title="Search Query"), user_id: str = "guest"):
    """🔎 Search for movies based on title, genre, or actor."""

    if not postgres_conn or not postgres_cursor:
        return {"error": "Database connection failed"}

    #  Save Search Query
    try:
        postgres_cursor.execute("""
            INSERT INTO user_search_history (user_id, search_query)
            VALUES (%s, %s);
        """, (user_id, q))
        postgres_conn.commit()
    except Exception as e:
        return {"error": f"Failed to save search history: {e}"}

    # **LOG DEBUG INFO BEFORE QUERY EXECUTION**
    print(f"🔍 Searching for: {q}")

    # **Improved Search Query**
    sql_query = """
        SELECT id, title, genre, rating, sentiment_score, actors 
        FROM movies
        WHERE LOWER(title) ILIKE %s 
        OR EXISTS (SELECT 1 FROM unnest(genre) AS g WHERE LOWER(g) ILIKE %s)  
        OR EXISTS (SELECT 1 FROM unnest(actors) AS a WHERE LOWER(a) ILIKE %s)
        ORDER BY sentiment_score DESC
        LIMIT 10;
    """
    query_params = (f"%{q.lower()}%", f"%{q.lower()}%", f"%{q.lower()}%")

    print(f"📝 SQL Query: {sql_query}")
    print(f"📌 Parameters: {query_params}")

    #  **Run SQL Query**
    try:
        postgres_cursor.execute(sql_query, query_params)
        movies = postgres_cursor.fetchall()

        #  LOG DEBUG INFO AFTER QUERY EXECUTION
        print(f"🔎 Raw SQL Output: {movies}")

        if not movies:
            print("❌ No movies found!")
            return {"message": "No movies found for your search!"}

        print(f" Found {len(movies)} movies for search: {q}")

        #  Convert Output to JSON Response
        movies_list = []
        for movie in movies:
            movies_list.append({
                "id": movie[0],
                "title": movie[1],
                "genre": movie[2],  
                "rating": movie[3],
                "sentiment_score": movie[4],
                "actors": movie[5]
            })

        return {"results": movies_list}

    except Exception as e:
        return {"error": f"Search failed: {e}"}


@app.get("/recommend")
def recommend_movies(user_id: str = "guest"):
    """🎯 Recommend movies based on past searches."""

    if not postgres_conn or not postgres_cursor:
        return {"error": "Database connection failed"}

    try:
        #  Fetch User’s Search History
        postgres_cursor.execute("""
            SELECT LOWER(search_query) FROM user_search_history
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 5;
        """, (user_id,))
        
        raw_searches = [row[0] for row in postgres_cursor.fetchall()]  

        if not raw_searches:
            return {"message": "No search history found!"}

        print(f"🔍 Raw Search History: {raw_searches}")

    except Exception as e:
        postgres_conn.rollback()
        return {"error": f"Failed to fetch search history: {e}"}

    try:
        #  Fetch genres from movies using a subquery
        postgres_cursor.execute("""
            SELECT DISTINCT g 
            FROM (SELECT unnest(genre) AS g FROM movies) subquery
            WHERE LOWER(g) IN %s;
        """, (tuple(raw_searches),))
        
        matched_genres = [row[0] for row in postgres_cursor.fetchall()]

        #  Fetch actors from movies
        postgres_cursor.execute("""
            SELECT DISTINCT a 
            FROM (SELECT unnest(actors) AS a FROM movies) subquery
            WHERE LOWER(a) IN %s;
        """, (tuple(raw_searches),))

        matched_actors = [row[0] for row in postgres_cursor.fetchall()]

        valid_searches = matched_genres + matched_actors

        if not valid_searches:
            return {"message": "No recommendations found based on your history."}

        print(f" Valid Searches Used for Recommendation: {valid_searches}")

    except Exception as e:
        postgres_conn.rollback()
        return {"error": f"Error filtering valid searches: {e}"}

    try:
        # Fetch recommended movies
        postgres_cursor.execute("""
            SELECT id, title, genre, rating, sentiment_score, actors 
            FROM movies
            WHERE genre && %s::TEXT[]
            OR actors && %s::TEXT[]
            ORDER BY sentiment_score DESC
            LIMIT 10;
        """, (valid_searches, valid_searches))

        recommended_movies = postgres_cursor.fetchall()

        if not recommended_movies:
            return {"message": "No recommendations found based on your history."}

        return {"recommendations": [
            {"id": m[0], "title": m[1], "genre": m[2], "rating": m[3], "sentiment_score": m[4], "actors": m[5]}
            for m in recommended_movies
        ]}

    except Exception as e:
        postgres_conn.rollback()
        return {"error": f"Recommendation failed: {e}"}
