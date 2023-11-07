from django.urls import include, path
from rest_framework import routers

from api.views import (RegisterViewSet, UserReceiveTokenViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', RegisterViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('auth/token/', UserReceiveTokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('', include(router.urls))
]
