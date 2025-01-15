from django.urls import path

from .views import ArticleDetailView, ArticleListView, LatestArticlesFeed

app_name = "BlogApp"

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticlesFeed(), name="articles-feed"),
]
