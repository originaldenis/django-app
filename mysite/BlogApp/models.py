from django.db import models
from django.urls import reverse


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("BlogApp:article", kwargs={"pk": self.pk})
