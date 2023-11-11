from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CommentViewSet,
    TitleViewSet,
    GenreViewSet,
    CategoryViewSet,
    RegisterViewSet,
    ReviewViewSet,
    UserRecieveTokenViewSet,
    UserViewSet,
)

s_router_v1 = SimpleRouter()
s_router_v1.register(r'titles', TitleViewSet, basename='titles')
s_router_v1.register(r'users', UserViewSet, basename='users')
s_router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
s_router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
s_router_v1.register(r'genres', GenreViewSet, basename='genres')     # Change when views are ready
s_router_v1.register(r'categories', CategoryViewSet, basename='categories')  # Change when views are ready

auth_urls = [
    path('signup/', RegisterViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('token/', UserRecieveTokenViewSet.as_view({'post': 'create'}),
         name='token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/', include(s_router_v1.urls)),
]
