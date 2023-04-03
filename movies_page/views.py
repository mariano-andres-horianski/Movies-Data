from gc import collect
from http.client import HTTPResponse
from pipes import Template
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from asgiref.sync import async_to_sync

import json
from .functions import shallow_search 
import requests, asyncio, aiohttp
from .forms import SearchForm, TitleForm, AddedTitleForm
from .models import AddedTitleModel, TitleModel

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
            # As of now, I'm only looking to use this forms to make the requested search (which may be cached later with redis)
            # and not store any data. 
            query = form.cleaned_data.get("query")
            endpoint = form.cleaned_data.get("search_type")
            text = shallow_search(endpoint=endpoint, query=query)
        
        form = SearchForm()
        
        return render(request, "movies_data/shallow_search.html", {'form': form, 'results':text['results']})

async def make_request(session, url):
    # Use aiohttp non-blocking version of requests.get()
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
    api_key = config('API_KEY')
    
    async with aiohttp.ClientSession() as session:
        for title in titles_list:
            url = f"https://imdb-api.com/en/API/Title/{api_key}/{title}"
            IMDB_requests.append(asyncio.ensure_future(make_request(session, url)))
            
        titles_res = await asyncio.gather(*IMDB_requests)
    return titles_res

@login_required
def titles_list_view(request):
    # Do the synchronous part of the process in this function
    if request.method == "POST":
        title_id = request.POST.get("id")

        if not TitleModel.objects.filter(id=title_id).exists():
            form = TitleForm(data=request.POST)
            if form.is_valid():
                title_data = shallow_search("Title", title_id)
                title = form.save(commit=False)
                title.title_data = title_data
                title.save()

                title = TitleModel.objects.get(id=title_id)
                AddedTitleModel.objects.create(owner=request.user, title=title)

                return redirect("movies_page:titles-list")

    # Retrieve the titles added by the user
    added_titles = AddedTitleModel.objects.filter(owner=request.user)

    # Create a list of the ids of the added titles
    titles_ids = [title.title.id for title in added_titles]

    # Manually request each title in order to retrieve information that was not provided by the shallow search.
    titles_data = async_to_sync(collect_requests)(titles_ids)

    return render(request, "movies_data/titles_list.html", {"titles_data": titles_data})

def delete_title(request, id):
    title = TitleModel.objects.filter(id=id)
    title = AddedTitleModel.objects.get(owner=request.user, title_id=id)
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
