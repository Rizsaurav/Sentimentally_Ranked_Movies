import scrapy

class Info(scrapy.Item):
    title = scrapy.Field()
    movie_rank = scrapy.Field()
    release_year = scrapy.Field()
    movie_length = scrapy.Field()
    rating = scrapy.Field()
    vote_count = scrapy.Field()
    description = scrapy.Field()
    imdb_id = scrapy.Field()
