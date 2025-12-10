from django.contrib import admin
from django.utils import timezone
from .models import Tag, BlogPost, PostView


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_private', 'author', 'published_at', 'view_count')
    list_filter = ('status', 'is_private', 'tags', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('author',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Classification', {
            'fields': ('author', 'tags', 'status', 'is_private')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )

    def view_count(self, obj):
        return obj.views.count()
    view_count.short_description = 'Views'

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        if obj.status == BlogPost.Status.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('post__title', 'ip_address')
    date_hierarchy = 'viewed_at'
    readonly_fields = ('post', 'ip_address', 'user_agent', 'viewed_at')
