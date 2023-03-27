from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

app_name = 'users'
router = DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    #path('users/', SubscriptionsViewSet.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
