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
            return response.json()

        response = requests.request("GET", url)
        cache.set(url, response, 3600)
        return response.json()