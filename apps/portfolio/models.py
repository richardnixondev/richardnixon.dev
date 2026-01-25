from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Technology(models.Model):
    """Technology/skill used in projects."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Icon class (e.g., devicon-python-plain)')
    color = models.CharField(max_length=7, default='#6366f1', help_text='Hex color code')

    class Meta:
        verbose_name_plural = 'Technologies'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    """Portfolio project."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    tagline = models.CharField(max_length=200, help_text='Short one-line description')
    description = models.TextField(help_text='HTML content')
    featured_image = models.ImageField(upload_to='portfolio/images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='portfolio/thumbnails/', blank=True, null=True)

    technologies = models.ManyToManyField(Technology, blank=True, related_name='projects')

    # Links
    live_url = models.URLField(blank=True, help_text='Live demo URL')
    github_url = models.URLField(blank=True, help_text='GitHub repository URL')
    documentation_url = models.URLField(blank=True, help_text='Documentation URL')

    # Display settings
    is_featured = models.BooleanField(default=False, help_text='Show on homepage')
    order = models.IntegerField(default=0, help_text='Display order (lower = first)')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, help_text='Leave blank if ongoing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:project_detail', kwargs={'slug': self.slug})

    @property
    def is_ongoing(self):
        return self.end_date is None


class ProjectImage(models.Model):
    """Additional images for a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='portfolio/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"
