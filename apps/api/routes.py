from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router, Query

from apps.blog.models import BlogPost, Tag
from apps.portfolio.models import Project, Technology
from apps.contact.models import ContactMessage, Resume
from .schemas import (
    TagSchema, PostListSchema, PostDetailSchema, RelatedPostSchema,
    TechnologySchema, ProjectListSchema, ProjectDetailSchema,
    ContactSubmitSchema, ContactResponseSchema, ResumeSchema,
    HomeDataSchema,
)

blog_router = Router(tags=["blog"])
portfolio_router = Router(tags=["portfolio"])
contact_router = Router(tags=["contact"])
home_router = Router(tags=["home"])


# ---- Home ----

@home_router.get("/", response=HomeDataSchema)
def home(request):
    posts = (
        BlogPost.objects.filter(status="published", is_private=False)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-published_at")[:5]
    )
    return {"recent_posts": posts}


# ---- Blog ----

@blog_router.get("/posts", response=list[PostListSchema])
def list_posts(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    search: str = Query(""),
    tag: str = Query(""),
):
    qs = (
        BlogPost.objects.filter(status="published", is_private=False)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-published_at")
    )
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(content__icontains=search)
            | Q(tags__name__icontains=search)
        ).distinct()
    if tag:
        qs = qs.filter(tags__slug=tag)

    offset = (page - 1) * page_size
    return qs[offset : offset + page_size]


@blog_router.get("/posts/count", response={200: int})
def posts_count(request, search: str = Query(""), tag: str = Query("")):
    qs = BlogPost.objects.filter(status="published", is_private=False)
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(content__icontains=search)
            | Q(tags__name__icontains=search)
        ).distinct()
    if tag:
        qs = qs.filter(tags__slug=tag)
    return qs.count()


@blog_router.get("/posts/{slug}", response=PostDetailSchema)
def get_post(request, slug: str):
    post = get_object_or_404(
        BlogPost.objects.select_related("author").prefetch_related("tags"),
        slug=slug,
        status="published",
    )
    return post


@blog_router.get("/posts/{slug}/related", response=list[RelatedPostSchema])
def related_posts(request, slug: str):
    post = get_object_or_404(BlogPost, slug=slug, status="published")
    related = (
        BlogPost.objects.filter(
            status="published", is_private=False, tags__in=post.tags.all()
        )
        .exclude(pk=post.pk)
        .distinct()[:3]
    )
    return related


@blog_router.get("/tags", response=list[TagSchema])
def list_tags(request):
    return Tag.objects.all().order_by("name")


# ---- Portfolio ----

@portfolio_router.get("/projects", response=list[ProjectListSchema])
def list_projects(request, tech: str = Query("")):
    qs = (
        Project.objects.filter(status="published")
        .prefetch_related("technologies")
        .order_by("order", "-created_at")
    )
    if tech:
        qs = qs.filter(technologies__slug=tech)
    return qs


@portfolio_router.get("/projects/featured", response=list[ProjectListSchema])
def featured_projects(request):
    return (
        Project.objects.filter(status="published", is_featured=True)
        .prefetch_related("technologies")
        .order_by("order")[:3]
    )


@portfolio_router.get("/projects/{slug}", response=ProjectDetailSchema)
def get_project(request, slug: str):
    return get_object_or_404(
        Project.objects.prefetch_related("technologies", "images"),
        slug=slug,
        status="published",
    )


@portfolio_router.get("/projects/{slug}/related", response=list[ProjectListSchema])
def related_projects(request, slug: str):
    project = get_object_or_404(Project, slug=slug, status="published")
    related = (
        Project.objects.filter(
            status="published", technologies__in=project.technologies.all()
        )
        .exclude(pk=project.pk)
        .prefetch_related("technologies")
        .distinct()[:3]
    )
    return related


@portfolio_router.get("/technologies", response=list[TechnologySchema])
def list_technologies(request):
    return Technology.objects.all().order_by("name")


# ---- Contact ----

@contact_router.post("/submit", response=ContactResponseSchema)
def submit_contact(request, data: ContactSubmitSchema):
    msg = ContactMessage.objects.create(
        name=data.name,
        email=data.email,
        subject=data.subject,
        message=data.message,
        ip_address=request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        referrer=request.META.get("HTTP_REFERER", ""),
    )
    if msg.is_likely_spam:
        msg.status = "spam"
        msg.save()
    return {"success": True, "message": "Message sent successfully."}


@contact_router.get("/resume", response={200: ResumeSchema, 404: ContactResponseSchema})
def get_resume(request):
    resume = Resume.objects.filter(is_active=True).first()
    if not resume:
        return 404, {"success": False, "message": "No resume available."}
    resume.increment_download()
    return resume
