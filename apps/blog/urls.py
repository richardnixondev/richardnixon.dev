from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.PostListView.as_view(), name='post_list'),
    path('blog/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('blog/tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('feed/', views.LatestPostsFeed(), name='feed'),
]
