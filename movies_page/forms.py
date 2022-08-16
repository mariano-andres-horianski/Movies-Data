from django import forms

SEARCH_TYPE = (
    ("Search", "Search anything"),
    ("SearchSeries", "Search TV shows only"),
    ("SearchMovie", "Search movies only"),
    ("SearchName", "Search people only"),
)

class SearchForm(forms.Form):
    """Form to send the text to search for."""
    query = forms.CharField()
    search_type = forms.ChoiceField(choices=SEARCH_TYPE)
