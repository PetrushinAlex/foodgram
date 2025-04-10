from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'users'

router = routers.DefaultRouter()

router.register(
    'users', 
    views.CustomUserViewSet, 
    basename='users'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
