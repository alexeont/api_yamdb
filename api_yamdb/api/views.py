from django.shortcuts import render
from rest_framework import viewsets

from .serializers import ReviewSerializer, CommentSerializer
from reviews.models import Comment, Review


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    #permission_classes =

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    #permission_classes =

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
