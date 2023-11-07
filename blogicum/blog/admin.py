from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'author',
        'location',
        'pub_date',
        'is_published',
        'display_image'
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
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'text',
                'pub_date',
                'author',
                'location',
                'category',
                'image'
            ),
        }),
        ('Публикация', {
            'fields': (
                'is_published',
            ),
        }),
    )

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.image.url
            )
        return "Нет изображения!"

    display_image.short_description = 'Изображение'


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
admin.site.register(Comment)
