from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'author',
        'location',
        'pub_date',
        'is_published'
    )
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = (
        'is_published',
        'pub_date',
        'category',
        'author',
        'location',
    )
    list_display_links = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published'
    )
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


admin.site.register(Location)
