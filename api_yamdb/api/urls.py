from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from .views import (
    TitleViewSet,
    GenreViewSet,
    GenreDestroyViewSet,
    CategoryViewSet,
    CategoryDestroyViewSet
)
(RegisterViewSet, UserRecieveTokenViewSet, UserViewSet)

router = SimpleRouter()
router.register(r'titles', TitleViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/genres/',
         GenreViewSet.as_view()),
    path('v1/categories/',
         CategoryViewSet.as_view()),
    path('v1/genres/<slug:genre_slug>/',
         GenreDestroyViewSet.as_view()),
    path('v1/categories/<slug:category_slug>/',
         CategoryDestroyViewSet.as_view())
]

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', RegisterViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('auth/token/', UserRecieveTokenViewSet.as_view({'post': 'create'}),
         name='token'),
    path('', include(router.urls))

]
