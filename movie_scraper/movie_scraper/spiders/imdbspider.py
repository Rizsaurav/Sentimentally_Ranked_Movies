import scrapy
from movie_scraper.items import Info  # Ensure this matches your project structure

class ImdbSpider(scrapy.Spider):
    name = "imdbspider"
    allowed_domains = ["imdb.com"]
    start_urls = [
        "https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&start=1"
    ]

    # ✅ Define User-Agent to prevent blocks
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "FEEDS": {
            "imdb_top250.json": {"format": "json", "encoding": "utf8"},
        },
    }

    def parse(self, response):
        """Extracts movie details from IMDb's Top 1000 list."""
        movies = response.css("div.lister-item.mode-advanced")

        for movie in movies:
            item = Info()
            item["title"] = movie.css("h3.lister-item-header a::text").get()
            item["year"] = movie.css("span.lister-item-year::text").get().strip()
            item["rating"] = movie.css("div.ratings-imdb-rating strong::text").get()
            item["duration"] = movie.css("span.runtime::text").get()
            item["genre"] = movie.css("span.genre::text").get().strip() if movie.css("span.genre::text").get() else None
            item["director"] = movie.css("p:nth-child(3) a::text").get()
            item["stars"] = movie.css("p:nth-child(3) a::text").getall()[1:]  # Get all actors
            yield item

        # ✅ Handle Pagination (Scrape Next Pages Until 250 Movies)
        next_page = response.css("a.lister-page-next.next-page::attr(href)").get()
        
        if next_page and "start=251" not in next_page:  # ✅ Stop after 250 movies
            yield response.follow(next_page, self.parse)
