from django.urls import path
from . import views

urlpatterns = [
    path('delete_blog_admin/', views.delete_blog_admin, name='delete_blog_admin'),
    path('update_blog/', views.update_blog, name='update_blog'),
    path('add_blog/', views.add_blog, name='add_blog')
]
