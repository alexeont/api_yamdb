from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import (
    CommentViewSet,
    TitleViewSet,
    GenreViewSet,
    GenreDestroyViewSet,
    CategoryViewSet,
    CategoryDestroyViewSet,
    RegisterViewSet,
    ReviewViewSet,
    UserRecieveTokenViewSet,
    UserViewSet,
)

s_router_v1 = SimpleRouter()
s_router_v1.register(r'titles', TitleViewSet)  # Full

d_router_v1 = DefaultRouter()
d_router_v1.register('users', UserViewSet, basename='users')
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

urlpatterns = [
    path('v1/genres/',
         GenreViewSet.as_view()),
    path('v1/categories/',
         CategoryViewSet.as_view()),
    path('v1/genres/<slug:genre_slug>/',
         GenreDestroyViewSet.as_view()),
    path('v1/categories/<slug:category_slug>/',
         CategoryDestroyViewSet.as_view()),
    path('v1/', include(s_router_v1.urls)),
    path('auth/signup/', RegisterViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('auth/token/', UserRecieveTokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('', include(d_router_v1.urls)),
]
