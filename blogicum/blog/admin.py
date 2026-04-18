from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'is_published',
        'description',
    )
    list_editable = (
        'title',
        'slug',
        'is_published',
        'description',
    )
    search_fields = ('slug', 'title')


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'is_published'
    )
    list_editable = (
        'name',
        'is_published'
    )
    search_fields = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'is_published',
        'pub_date',
        'text',
    )
    list_editable = (
        'is_published',
        'title',
        'text',
        'pub_date',
    )
    search_fields = ('title',)
    list_filter = ('is_published', )


admin.site.empty_value_display = 'Не задано'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
