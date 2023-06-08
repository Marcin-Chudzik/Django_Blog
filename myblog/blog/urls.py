from django.urls import path
from . import views
from . import feeds

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post-list-by-tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post_slug>/',
         views.post_detail, name='post-detail'),
    path('feed/', feeds.LatestPostsFeed(), name='post-feed'),
]
