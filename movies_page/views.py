from django.shortcuts import render
from django.views.generic import FormView
from django.core.cache import cache
from django.conf import settings
import requests
from .forms import SearchForm

from decouple import config

def home(request):
    return render(request, "movies_data/home.html")

class ShallowSearchView(FormView):
    template_name = "movies_data/shallow_search.html"
    form_class = SearchForm
    api_key = config('API_KEY')

    def shallow_search(self, query, endpoint="Search"):
        """
        Make the request based on SearchSeries, SearchMovie or SearchName endpoints.
        Default is Search, which includes all three of them.
        """
        url = f"https://imdb-api.com/en/API/{endpoint}/{self.api_key}/{query}"
        if cache.get(url):
            response = cache.get(url)
            return response.json()

        response = requests.request("GET", url)
        cache.set(url, response, 300)
        return response.json()

    def get_context_data(self, **kwargs):
        context = super(ShallowSearchView, self).get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context

    def post(self, request):
        
        form = SearchForm(request.POST)

        if form.is_valid():
            #As of now, I'm only looking to use this forms to make the requested search (which may be cached later with redis)
            # and not store any data. 
            query = form.cleaned_data.get("query")
            endpoint = form.cleaned_data.get("search_type")
            text = self.shallow_search(query, endpoint=endpoint)
        
        form = SearchForm()

        return render(request, "movies_data/shallow_search.html", {'form': form, 'results':text['results']})

def get_trending(request):
    """
    Render a page with the most popular titles last week.
    """
    pass

def get_score(request):
    """
    Get the score of a title and update it.
    """
    pass

def get_voters_number(request):
    """
    Get the number of voters for a title's score and update it.
    """
    pass