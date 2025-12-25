from django.db import models
from django.conf import settings


class ContactMessage(models.Model):
    """Contact form submission."""

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        READ = 'read', 'Read'
        REPLIED = 'replied', 'Replied'
        SPAM = 'spam', 'Spam'
        ARCHIVED = 'archived', 'Archived'

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)

    # Spam detection
    honeypot = models.CharField(max_length=200, blank=True, help_text='Hidden field for spam detection')
    submission_time = models.FloatField(default=0, help_text='Time taken to submit form in seconds')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject}"

    @property
    def is_likely_spam(self):
        """Basic spam detection heuristics."""
        # Honeypot filled
        if self.honeypot:
            return True
        # Form submitted too quickly (less than 3 seconds)
        if self.submission_time > 0 and self.submission_time < 3:
            return True
        # Check for common spam patterns
        spam_keywords = ['viagra', 'casino', 'crypto', 'bitcoin', 'lottery', 'prize']
        content = f"{self.subject} {self.message}".lower()
        if any(keyword in content for keyword in spam_keywords):
            return True
        return False


class Resume(models.Model):
    """Uploaded resume/CV for download."""
    title = models.CharField(max_length=100, default='Resume')
    file = models.FileField(upload_to='resumes/')
    is_active = models.BooleanField(default=True)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])
