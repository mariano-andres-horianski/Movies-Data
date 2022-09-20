from gc import collect
from http.client import HTTPResponse
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from asgiref.sync import async_to_sync

from .functions import shallow_search 
import requests, asyncio, aiohttp
from .forms import SearchForm, TitleForm
from .models import TitleModel

from decouple import config

def home(request):
    return render(request, "movies_data/home.html")

class ShallowSearchView(FormView):
    template_name = "movies_data/shallow_search.html"
    form_class = SearchForm
    api_key = config('API_KEY')

    def post(self, request):
        
        form = SearchForm(request.POST)

        if form.is_valid():
            #As of now, I'm only looking to use this forms to make the requested search (which may be cached later with redis)
            # and not store any data. 
            query = form.cleaned_data.get("query")
            endpoint = form.cleaned_data.get("search_type")
            text = shallow_search(endpoint=endpoint, query=query)
        
        form = SearchForm()

        return render(request, "movies_data/shallow_search.html", {'form': form, 'results':text['results']})

async def make_request(session, url):
    #Use aiohttp non-blocking version of requests.get()
    async with session.get(url) as res:
        movies_data = await res.json()
        return movies_data

async def collect_requests(titles_list):
    """
    From a list of titles, request additional data about them.
    A view created mainly with the purpose of using asyncio and Django async functions for learning,
    also useful for not having to save data that may change over time (such as rating or voters number).
    """
    IMDB_requests = []
    titles_data = []
    api_key = config('API_KEY')

    async with aiohttp.ClientSession() as session:
        for title in titles_list:
            title_id = title.id
            url = f"https://imdb-api.com/en/API/Title/{api_key}/{title_id}"
            IMDB_requests.append(asyncio.ensure_future(make_request(session, url)))
            
        titles_res = await asyncio.gather(*IMDB_requests)
        
    for data in titles_res:
        titles_data.append(data)
    
    return titles_data

@login_required
def titles_list_view(request):
    #Do the synchronous part of the process in this function
    if request.method == "POST":
        form = TitleForm(data=request.POST)
        if form.is_valid():
            title = form.save(commit=False)
            title.save()
            title.owner.add(request.user)
            return redirect("movies_page:titles-list")

    titles_list = TitleModel.objects.filter(owner=request.user)
    
    #Move the async parts of the process away
    titles_data = async_to_sync(collect_requests)(list(titles_list))
    return render(request, "movies_data/titles_list.html", {"titles_data": titles_data})
    
def delete_title(request, id):
    title = TitleModel.objects.filter(id=id, owner=request.user)
    title.delete()
    return redirect("movies_page:titles-list")

class TrendingView(TemplateView):
    """
    Render a view with the most popular titles.
    It also serves as a wrapper for get_trending function.
    """
    template_name = "movies_data/trending.html"
    api_key = config('API_KEY')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trending_movies"] = shallow_search("MostPopularMovies")["items"]
        context["trending_series"] = shallow_search("MostPopularTVs")["items"]
        return context

def set_score(request):
    """
    Put a personal score on a title.
    """
    pass