from django.urls import path
from . import views

app_name = 'movies_page'

urlpatterns = [
    path("", views.home, name='home'),
    path("search/", views.ShallowSearchView.as_view(), name='shallow_search'),
]