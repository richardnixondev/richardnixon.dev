from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify
from django.utils.html import strip_tags


class Tag(models.Model):
    """Tag for categorizing blog posts."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    """Blog post with markdown content."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField(blank=True, help_text='Short description for listings')
    content = models.TextField(help_text='HTML content')
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    is_private = models.BooleanField(default=False, help_text='Only visible to owner')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            # Strip HTML tags for excerpt
            plain_text = strip_tags(self.content)
            self.excerpt = plain_text[:200] + '...' if len(plain_text) > 200 else plain_text
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def content_html(self):
        """Return HTML content from CKEditor."""
        return self.content

    @property
    def reading_time(self):
        """Estimate reading time in minutes."""
        plain_text = strip_tags(self.content)
        word_count = len(plain_text.split())
        return max(1, round(word_count / 200))


class PostView(models.Model):
    """Track post views for analytics."""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
