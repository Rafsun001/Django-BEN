from django.contrib import admin
from .models import Blog, Comment, CommentLike, LoveReactShow, ReadStatus


class BlogAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "banner", "read", "timestamp", "views", "love_react", "comment_count", "html_field"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "blog", "user", "parent", "comment_text", "timestamp", "like_count"]


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "comment","comment_flag"]


class LoveReactShowAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "blog", "love_react"]


class ReadStatusAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "blog", "read_sts"]


admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
admin.site.register(LoveReactShow, LoveReactShowAdmin)
admin.site.register(ReadStatus, ReadStatusAdmin)
