from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CommentViewSet,
    TitleViewSet,
    GenreViewSet,
    CategoryViewSet,
    UserRegisterApiView,
    ReviewViewSet,
    UserRecieveTokenApiView,
    UserViewSet,
)

s_router_v1 = SimpleRouter()
s_router_v1.register(r'titles', TitleViewSet)
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
s_router_v1.register(
    r'genres',
    GenreViewSet
)
s_router_v1.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)

urlpatterns = [
    path('v1/auth/signup/', UserRegisterApiView.as_view(),
         name='signup'),
    path('v1/auth/token/', UserRecieveTokenApiView.as_view(),
         name='token'),
    path('v1/', include(s_router_v1.urls)),
]
