from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .serializers import *
from django.contrib.auth.models import User
from .models import *
import random
import string
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

@csrf_exempt
@api_view(['POST'])
def get_blog_details(request):
    blog_id = request.data.get('blog_id')

    try:
        blog = Blog.objects.get(pk=blog_id)
        blog.refresh_from_db()
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BlogDetailSerializer(blog, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def add_comment_or_reply(request):
    """
    Add a new comment or reply to a blog.
    Frontend sends:
        - blog_id (required)
        - comment_text (required)
        - parent_id (optional; if provided, it's a reply)
    """
    user = request.user
    blog_id = request.data.get('blog_id')
    comment_text = request.data.get('comment_text')
    parent_id = request.data.get('parent_id', None)

    # Basic validation
    if not blog_id or not comment_text:
        return Response({"error": "blog_id and comment_text are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Fetch blog
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found."},
                        status=status.HTTP_404_NOT_FOUND)

    # If replying to a comment
    parent_comment = None
    if parent_id:
        try:
            parent_comment = Comment.objects.get(id=parent_id)
        except Comment.DoesNotExist:
            return Response({"error": "Parent comment not found."},
                            status=status.HTTP_404_NOT_FOUND)

    # Create new comment or reply
    new_comment = Comment.objects.create(
        blog=blog,
        user=user,
        parent=parent_comment,
        comment_text=comment_text,
        timestamp=timezone.now()
    )

    # Update blog's total comment count
    blog.comment_count = blog.comment_count + 1
    blog.save(update_fields=["comment_count"])

    # Serialize response (so frontend gets comment info immediately)
    serializer = CommentSerializer(new_comment, context={"request": request})

    return Response({
        "message": "Comment added successfully.",
        "comment_count": blog.comment_count,
        "comment": serializer.data
    }, status=status.HTTP_201_CREATED)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def like_unlike_comment(request):
    """
    Toggle like/unlike on a comment or reply.
    Frontend sends:
        - comment_id
        - like_status (1 = like, 0 = unlike)
    """
    user = request.user
    comment_id = request.data.get("comment_id")
    like_status = request.data.get("like_status")

    if not comment_id or like_status is None:
        return Response({"error": "comment_id and like_status are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        like_status = int(like_status)
    except ValueError:
        return Response({"error": "like_status must be 0 or 1"}, status=status.HTTP_400_BAD_REQUEST)

    if like_status not in [0, 1]:
        return Response({"error": "like_status must be 0 or 1"}, status=status.HTTP_400_BAD_REQUEST)

    like_obj = CommentLike.objects.filter(user=user, comment=comment).first()

    if like_obj:
        # User already liked this comment
        if like_status == 0:
            # Unlike it
            like_obj.delete()
            comment.like_count = max(comment.like_count - 1, 0)
    else:
        # New like
        if like_status == 1:
            CommentLike.objects.create(user=user, comment=comment)
            comment.like_count += 1

    comment.save(update_fields=['like_count'])

    return Response({
        "comment_id": comment.id,
        "like_status": like_status,
        "like_count": comment.like_count
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def blog_read_status(request):
    user = request.user
    blog_id = request.data.get('blog_id')

    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
    
    read_obj = ReadStatus.objects.filter(user=user, blog=blog).first()

    if not read_obj:
        # Create new read record
        ReadStatus.objects.create(user=user, blog=blog, read_sts="Read")
        status_text = "Read"
    else:
        # Already read
        status_text = read_obj.read_sts

    return Response({
        "blog_id": blog.id,
        "read_status": status_text
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def viewscount(request):
    blog_id = request.data.get('blog_id')

    blog_tbl = Blog.objects.get( id = blog_id)
    blog_tbl.views += 1
    return Response({
        "view_count":blog_tbl.views
        },
        status=status.HTTP_200_OK
        )

@api_view(['POST'])
def count_parent_comments(request):
    blog_id = request.data.get('blog_id')
    blog = Blog.objects.get(pk=blog_id)
    parent_comment_count = Comment.objects.filter(blog=blog, parent__isnull=True).count()
    return Response(
        {
            "blog_id": blog.id,
            "blog_title": blog.title,
            "total_parent_comments": parent_comment_count
        },
        status=status.HTTP_200_OK
    )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def react_yes_no(request):
    
    user = request.user
    blog_id = request.data.get('blog_id')
    react_status = request.data.get('react_status')

    blog = Blog.objects.get(id=blog_id)
    
    react_obj = LoveReactShow.objects.filter(user=user, blog=blog).first()

    if react_obj:
        react_obj.love_react = react_status
        react_obj.save(update_fields=['love_react'])
    else:
        LoveReactShow.objects.create(user=user, blog=blog, love_react="1")

    return Response({
        "blog_id": blog.id,
        "reacted_by_user": react_status
    }, status=status.HTTP_200_OK)



class BlogPagination(PageNumberPagination):
    page_size = 5  # 5 blogs per page
    page_size_query_param = 'page_size'  # frontend can override (optional)
    max_page_size = 20


@api_view(['GET'])
def get_paginated_blogs(request):
    blogs = Blog.objects.all().order_by('-timestamp')  # latest first
    paginator = BlogPagination()
    paginated_blogs = paginator.paginate_queryset(blogs, request)
    serializer = BlogListSerializer(paginated_blogs, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_comment(request):
    comment_id = request.data.get("comment_id")
    comment_text = request.data.get("comment_text")
    
    if not comment_id or comment_text is None:
        return Response(
            {"error": "Both 'comment_id' and 'comment_text' are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    if comment.user != request.user:
        return Response(
            {"error": "You are not allowed to edit this comment"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = CommentSerializer(
        comment,
        data={"comment_text": comment_text},
        partial=True,
        context={"request": request}  # ✅ fix here
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Comment updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request):
    comment_id = request.data.get("comment_id")
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    # Only owner or admin can delete
    if comment.user != request.user and not request.user.is_staff:
        return Response({"error": "You are not allowed to delete this comment"}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({"message": "Comment deleted successfully"}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_comment_like(request):
    comment_id = request.data.get("comment_id")
    flag = request.data.get("flag")

    if flag not in [0, 1, "0", "1"] or not comment_id:
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user  # ✅ authenticated user object directly

    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

    like, _ = CommentLike.objects.get_or_create(user=user, comment=comment)
    like.comment_flag = flag
    like.save()

    return Response({
        "comment_id": comment.id,
        "user_id": user.id,
        "flag": flag
    }, status=status.HTTP_200_OK)
