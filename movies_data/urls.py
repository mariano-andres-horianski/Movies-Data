from django.contrib import admin
from django.urls import path, include

app_name = 'movies_data'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies_page.urls')),
    path('users/', include('users.urls')),
]
