from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'movies_page'

urlpatterns = [
    path("", views.home, name='home'),
    path("search/", views.ShallowSearchView.as_view(), name='shallow_search'),
    #add login require to titles list urls
    path("titles-list", views.titles_list_view, name='titles-list')
]