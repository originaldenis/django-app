from django.contrib.syndication.views import Feed
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from BlogApp.models import Article


class ArticleListView(ListView):
    template_name = "BlogApp/article_list.html"
    queryset = Article.objects.filter(pub_date__isnull=False).order_by("-pub_date")


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles(latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("BlogApp:articles")

    def items(self):
        return Article.objects.filter(pub_date__isnull=False).order_by("-pub_date")[:5]

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]

    # Так как указано в модели,то тут автоматически ссылка возьмется
    # def item_link(self, item: Article):
    #     return reverse("BlogApp:article", kwargs={"pk": item.pk})
