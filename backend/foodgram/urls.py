from django.contrib import admin
from django.urls import include, path

from food.views import redirect_recipe

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('recipes/<int:pk>/', redirect_recipe, name='redirect_recipe'),
]
