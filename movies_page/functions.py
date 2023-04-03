from django.core.cache import cache
import requests
from decouple import config
def shallow_search(endpoint="Search", query=""):
        """
        Make the request based on SearchSeries, SearchMovie or SearchName endpoints.
        Default is Search, which includes all three of them.
        """
        api_key = config('API_KEY')
        url = f"https://imdb-api.com/en/API/{endpoint}/{api_key}/{query}"
        if cache.get(url):
            response = cache.get(url)
            return response

        response = requests.request("GET", url).json()
        cache.set(url, response, 3600)
        return response

class Logger:
    __instance = None

    def __new__(cls):
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
            Logger.__instance.log_file = open("log.txt", "w")
        return Logger.__instance

    def log(self, message):
        self.log_file.write("movies_page app" + message + "\n")