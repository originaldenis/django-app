from django.contrib.sitemaps import Sitemap

from shopapp.models import Product


class ShopSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Product.objects.all().order_by("-price")
