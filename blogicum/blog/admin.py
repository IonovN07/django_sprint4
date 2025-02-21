from django.contrib import admin

from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'category',
        'created_at',
        'is_published',
        'location'
    )
    list_editable = (
        'is_published',
        'location',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category', 'author', 'location')
    list_display_links = ('title',)


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'is_published',
        'slug',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.empty_value_display = 'Не задано'
