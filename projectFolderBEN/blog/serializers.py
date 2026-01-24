from rest_framework import serializers
from .models import Blog, Comment
from authenticationAPP.views import Profile

class RecursiveField(serializers.Serializer):
    """Allows nested replies."""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class UserProfileInfoSerializer(serializers.ModelSerializer):
    """Minimal user info for comments."""
    class Meta:
        model = Profile
        fields = ['full_name', 'image']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    replies = RecursiveField(many=True, read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    like_flag = serializers.SerializerMethodField()  # ✅ NEW FIELD

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "comment_text",
            "timestamp",
            "like_count",
            "like_flag",  # ✅ add this
            "replies",
        ]

    def get_user(self, obj):
        """Return user's profile image and name."""
        try:
            profile = Profile.objects.get(user=obj.user)
            return {
                "username": obj.user.username,
                "full_name": profile.full_name,
                "image": self.context["request"].build_absolute_uri(profile.image.url)
                if profile.image else None
            }
        except Profile.DoesNotExist:
            return {
                "username": obj.user.username,
                "full_name": obj.user.get_full_name() or obj.user.username,
                "image": None
            }

    def get_like_flag(self, obj):
        """Return 1 if the authenticated user liked this comment, 0 if not, null if unauthenticated."""
        request = self.context.get('request')
        user = request.user

        if not user or not user.is_authenticated:
            return None  # unauthenticated users get null

        like_entry = obj.likes.filter(user=user).first()
        if like_entry and like_entry.comment_flag == "1":
            return 1
        return 0



class BlogDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "banner",
            "timestamp",
            "read",
            "title",
            "views",
            "love_react",
            "comment_count",
            "html_field",
            "author",
            "comments"
        ]

    def get_comments(self, obj):
        top_level_comments = obj.comments.filter(parent__isnull=True)
        serializer = CommentSerializer(top_level_comments, many=True, context=self.context)
        return serializer.data

    def get_author(self, obj):
        return {
            "name": "AI Ninjas Team",
            "image": self.context["request"].build_absolute_uri("/media/static_image/author_default.png")
        }


class BlogListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_image = serializers.SerializerMethodField()
    user_love_react = serializers.SerializerMethodField()  # ✅ new field

    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'banner',
            'timestamp',
            'views',
            'comment_count',
            'love_react',
            'author_name',
            'author_image',
            'user_love_react',  # ✅ include it
        ]

    def get_author_name(self, obj):
        return "AI Ninjas Team"

    def get_author_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri('/media/profile_pics/author_default.png')

    def get_user_love_react(self, obj):
        """Return the authenticated user's love react if exists."""
        request = self.context.get('request')
        user = request.user
        if not user.is_authenticated:
            return None  # unauthenticated users get no data

        react = obj.love_reacts.filter(user=user).first()
        if react:
            return react.love_react
        return None