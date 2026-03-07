import os
from datetime import datetime
from ninja import Schema

SITE_URL = os.environ.get("SITE_URL", "https://richardnixon.dev")


def _abs_url(field_file):
    if not field_file:
        return None
    return f"{SITE_URL}{field_file.url}"


# ---- Blog ----

class TagSchema(Schema):
    name: str
    slug: str
    description: str


class PostListSchema(Schema):
    id: int
    title: str
    slug: str
    excerpt: str
    featured_image: str | None
    tags: list[TagSchema]
    reading_time: int
    published_at: datetime | None
    author_name: str | None

    @staticmethod
    def resolve_featured_image(obj):
        return _abs_url(obj.featured_image)

    @staticmethod
    def resolve_author_name(obj):
        return obj.author.get_short_name() if obj.author else None


class PostDetailSchema(PostListSchema):
    content: str
    meta_description: str
    meta_keywords: str
    created_at: datetime
    updated_at: datetime


class RelatedPostSchema(Schema):
    title: str
    slug: str
    excerpt: str
    featured_image: str | None
    reading_time: int
    published_at: datetime | None

    @staticmethod
    def resolve_featured_image(obj):
        return _abs_url(obj.featured_image)


# ---- Portfolio ----

class TechnologySchema(Schema):
    name: str
    slug: str
    icon: str
    color: str


class ProjectListSchema(Schema):
    id: int
    title: str
    slug: str
    tagline: str
    featured_image: str | None
    thumbnail: str | None
    technologies: list[TechnologySchema]
    live_url: str
    github_url: str
    is_featured: bool
    is_ongoing: bool
    start_date: datetime | None
    end_date: datetime | None

    @staticmethod
    def resolve_featured_image(obj):
        return _abs_url(obj.featured_image)

    @staticmethod
    def resolve_thumbnail(obj):
        return _abs_url(obj.thumbnail)


class ProjectImageSchema(Schema):
    image: str
    caption: str
    order: int

    @staticmethod
    def resolve_image(obj):
        return _abs_url(obj.image)


class ProjectDetailSchema(ProjectListSchema):
    description: str
    documentation_url: str
    images: list[ProjectImageSchema]
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_images(obj):
        return obj.images.all().order_by('order')


# ---- Contact ----

class ContactSubmitSchema(Schema):
    name: str
    email: str
    subject: str
    message: str


class ContactResponseSchema(Schema):
    success: bool
    message: str


class ResumeSchema(Schema):
    title: str
    file_url: str

    @staticmethod
    def resolve_file_url(obj):
        return _abs_url(obj.file)


# ---- Home ----

class HomeDataSchema(Schema):
    recent_posts: list[PostListSchema]
