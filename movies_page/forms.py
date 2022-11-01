from django import forms

from .models import TitleModel, AddedTitleModel

SEARCH_TYPE = (
    ("Search", "Search anything"),
    ("SearchTitle", "Search movies or TV shows"),
    ("SearchSeries", "Search TV shows only"),
    ("SearchMovie", "Search movies only"),
    ("SearchName", "Search people only"),
)

class SearchForm(forms.Form):
    """Form to send the text to search for."""
    query = forms.CharField()
    search_type = forms.ChoiceField(choices=SEARCH_TYPE)

class TitleForm(forms.ModelForm):
    """Form to add a title to the DB for cache."""

    class Meta:
        model = TitleModel
        fields = ['id', 'title_data']

class AddedTitleForm(forms.ModelForm):
    """Form to add a title to the user's list."""

    class Meta:
        model = AddedTitleModel
        fields = ['owner', 'title']
