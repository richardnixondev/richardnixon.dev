from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import BlogPost, Tag, PostView


class PostListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)

        # Filter private posts unless user is owner
        if not self.request.user.is_authenticated or not getattr(self.request.user, 'is_owner', False):
            queryset = queryset.filter(is_private=False)

        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        return queryset.select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['active_tag'] = self.request.GET.get('tag', '')
        return context


class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)

        # Filter private posts unless user is owner
        if not self.request.user.is_authenticated or not getattr(self.request.user, 'is_owner', False):
            queryset = queryset.filter(is_private=False)

        return queryset.select_related('author').prefetch_related('tags')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Track view
        PostView.objects.create(
            post=obj,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        return obj

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related posts by tags
        post_tags = self.object.tags.all()
        context['related_posts'] = BlogPost.objects.filter(
            tags__in=post_tags,
            status=BlogPost.Status.PUBLISHED,
            is_private=False
        ).exclude(pk=self.object.pk).distinct()[:3]
        return context


class TagDetailView(ListView):
    model = BlogPost
    template_name = 'blog/tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        queryset = BlogPost.objects.filter(
            tags=self.tag,
            status=BlogPost.Status.PUBLISHED
        )

        if not self.request.user.is_authenticated or not getattr(self.request.user, 'is_owner', False):
            queryset = queryset.filter(is_private=False)

        return queryset.select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['tags'] = Tag.objects.all()
        return context


class LatestPostsFeed(Feed):
    title = "richardnixon.dev - Blog"
    link = "/blog/"
    description = "Latest posts from richardnixon.dev"

    def items(self):
        return BlogPost.objects.filter(
            status=BlogPost.Status.PUBLISHED,
            is_private=False
        ).order_by('-published_at')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.published_at


def home(request):
    """Homepage view."""
    recent_posts = BlogPost.objects.filter(
        status=BlogPost.Status.PUBLISHED,
        is_private=False
    ).select_related('author').prefetch_related('tags')[:5]

    return render(request, 'blog/home.html', {
        'recent_posts': recent_posts,
    })
