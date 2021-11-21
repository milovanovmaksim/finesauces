from django.contrib import admin

from .models import Category, Product, Review


class OrderReviewInline(admin.TabularInline):
    model = Review


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'price', 'available')
    list_filter = ('category', 'available')
    list_editable = ('price', 'available')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [OrderReviewInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)