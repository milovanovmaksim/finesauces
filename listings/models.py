from django.db import models
from django.urls import reverse
from django.db.models import Manager
from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator, MaxValueValidator


class ProductManager(Manager):
    def get_by_slug(self, product_slug, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        return get_object_or_404(Product, category_id=category.id, slug=product_slug)

    def get_by_category(self, category):
        queryset = self.filter(category=category)
        return queryset


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-name',)
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return reverse('listings:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    shu = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    objects = ProductManager()

    class Meta:
        ordering = ('shu',)

    def get_absolute_url(self):
        return reverse('listings:product_detail', args=[self.category.slug, self.slug])

    def get_average_review_score(self):
        average_score = 0.0
        if self.reviews.count() > 0:
            total_score = sum([review.rating for review in self.reviews.all()])
            average_score = total_score / self.reviews.count()
        return round(average_score, 1)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author = models.CharField(max_length=50)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
