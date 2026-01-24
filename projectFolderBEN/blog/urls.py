from django.urls import path
from . import views  # Import your views here

urlpatterns = [
    path('get_blog_details/', views.get_blog_details, name='get_blog_details'),
    path('add_comment_or_reply/', views.add_comment_or_reply, name='add_comment_or_reply'),
    path('like_unlike_comment/', views.like_unlike_comment, name='like_unlike_comment'),
    path('blog_read_status/', views.blog_read_status, name='blog_read_status'),
    path('viewscount/', views.viewscount, name='viewscount'),
    path('count_parent_comments/', views.count_parent_comments, name='count_parent_comments'),
    path('react_yes_no/', views.react_yes_no, name='react_yes_no'),
    path('blogs/', views.get_paginated_blogs, name='get_paginated_blogs'),
    path('edit_comment/', views.edit_comment, name='edit_comment'),
    path('delete_comment/', views.delete_comment, name='delete_comment'),
    path('update_comment_like/', views.update_comment_like, name='update_comment_like')
]