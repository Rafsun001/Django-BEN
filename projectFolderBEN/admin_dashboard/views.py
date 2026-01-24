from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from blog.models import Blog
from rest_framework.parsers import MultiPartParser, FormParser
import os

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # only staff/admins
def delete_blog_admin(request):
    blog_id = request.data.get('blog_id')

    if not blog_id:
        return Response({"error": "blog_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    blog.delete()
    return Response({"message": f"Blog '{blog.title}' deleted successfully."}, status=status.HTTP_200_OK)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # allows banner upload
def update_blog(request):
    user = request.user
    blog_id = request.data.get('blog_id')
    title = request.data.get('title')
    html_field = request.data.get('html_field')
    banner = request.FILES.get('banner')

    if not blog_id:
        return Response({"error": "blog_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Delete old banner if a new one is uploaded
    if banner and blog.banner:
        old_banner_path = blog.banner.path
        if os.path.exists(old_banner_path):
            os.remove(old_banner_path)

    # ✅ Update provided fields
    if title:
        blog.title = title
    if html_field:
        blog.html_field = html_field
    if banner:
        blog.banner = banner

    blog.save()

    return Response({
        "message": "Blog updated successfully.",
        "blog_id": blog.id,
        "title": blog.title,
        "banner": request.build_absolute_uri(blog.banner.url) if blog.banner else None,
        "html_field": blog.html_field,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # allows banner upload
def add_blog(request):
    """
    Create a new blog post.
    Requires authentication.
    """
    user = request.user
    title = request.data.get('title')
    html_field = request.data.get('html_field')
    banner = request.FILES.get('banner')

    # ✅ Basic validation
    if not title or not html_field:
        return Response(
            {"error": "Both 'title' and 'html_field' are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Create the new Blog object
    blog = Blog(
        title=title,
        html_field=html_field,
        banner=banner if banner else None,
    )

    blog.save()

    return Response({
        "message": "Blog created successfully.",
        "blog_id": blog.id,
        "title": blog.title,
        "banner": request.build_absolute_uri(blog.banner.url) if blog.banner else None,
        "html_field": blog.html_field,
    }, status=status.HTTP_201_CREATED)


