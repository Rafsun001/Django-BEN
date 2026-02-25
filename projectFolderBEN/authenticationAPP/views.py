from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .serializers import ProfileSerializer
from django.contrib.auth.models import User
from .models import Profile, GetInTouch
import random
import string
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
# Create your views here.

@csrf_exempt
@api_view(['POST'])
def signup(request):
    email = request.data.get('email')
    password = request.data.get('password')
    full_name = request.data.get('full_name')
    phone_number = request.data.get('phone_number')

    if not email or not password or not full_name or not phone_number:
        return Response({"message": "All fields (full_name, password, email, phone_number) are required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        existing_user = User.objects.get(username=email)
        if existing_user.is_active:
            return Response({"error": "This email is already registered and verified."}, status=400)
        else:
            existing_user.delete()
    except User.DoesNotExist:
        pass 

    user = User.objects.create_user(username=email, email=email, password=password)
    user.is_active = False
    user.save()

    profile = Profile.objects.create(user=user)
    otp = ''.join(random.choices(string.digits, k=4))
    profile.phone_number = phone_number
    profile.otp = otp
    profile.full_name = full_name
    profile.save()

    subject = 'Your OTP for Email Verification'
    message = f'Hello, your OTP to verify your email is: {otp}.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

    return Response({
        'message': 'successful',
    }, status=status.HTTP_201_CREATED)
    

@csrf_exempt
@api_view(['POST'])
def verify_otp(request):
    username = request.data.get('email')
    otp = request.data.get('otp')

    if not username or not otp:
        return Response({"Error": "Both Username and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        user_profile = Profile.objects.get(user=user)
    except User.DoesNotExist:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
    if user_profile.otp == otp:
        user.is_active = True
        user.save()
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        user_profile.save()
        return Response({
            'message': 'OTP verified successfully and tokens issued.'
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
    

@csrf_exempt
@api_view(['POST'])
def resend_otp(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(username=email)
        profile = Profile.objects.get(user=user)
    except:
        return Response(
            {"Message": "Invalid Email."},
            status=status.HTTP_400_BAD_REQUEST
        )

    otp = ''.join(random.choices(string.digits, k=4))
    profile.otp = otp
    profile.save()
    subject = 'Your OTP for Email Verification'
    message = f'Hello, your OTP to verify your email is: {otp}.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

    return Response({
        'message': 'Please verify OTP sent to your email.',
    }, status=status.HTTP_201_CREATED)  

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"message": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({"message": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    return Response({
        'refresh_token': str(refresh),
        'access_token': str(access_token),
        'profile_data': ProfileSerializer(user.profile).data,
        'message': 'Successfully authenticated.'
    },      status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')

    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=email)
        profile = Profile.objects.get(user=user)
        otp = ''.join(random.choices(string.digits, k=4))
        profile.otp = otp
        profile.save()

        subject = 'Your Password Reset OTP'
        message = f'Hello, your OTP to reset your password is: {otp}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Invalid email."}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
def verify_forgot_password_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    print(email, otp)
    if not email or not otp:
        return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=email)
        profile = Profile.objects.get(user=user)
        print(profile.otp)
        if profile.otp == otp:
            return Response({"message": "OTP is valid."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "Invalid email."}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('password')

    if not email or not new_password:
        return Response({"error": "Email and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=email)
        profile = Profile.objects.get(user=user)

        if not profile.otp:
            return Response({"error": "Please verify OTP first."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        profile.otp = None
        profile.save()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Invalid email."}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({"error": "Current and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    if not user.check_password(current_password):
        return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def verify_social_signup_signin_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response(
            {"error": "Email and OTP are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    email = email.strip().lower()
    otp = str(otp).strip()

    try:
        user = User.objects.select_related("profile").get(username=email)
        profile = user.profile
    except User.DoesNotExist:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
    except Profile.DoesNotExist:
        return Response({"error": "Profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Must have an OTP stored
    if not profile.otp:
        return Response(
            {"error": "No OTP found. Please request a new OTP."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify OTP
    if profile.otp != otp:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    # OTP correct ✅
    # If user is not active -> activate
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=["is_active"])

    # Clear OTP so it can't be reused
    profile.otp = None
    profile.save(update_fields=["otp"])

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "OTP verified successfully.",
        "refresh_token": str(refresh),
        "access_token": str(refresh.access_token),
        "profile_data": ProfileSerializer(profile).data,
    }, status=status.HTTP_200_OK)
    

@api_view(['PATCH'])
def get_in_touch(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    message = request.data.get('message')
    
    if not first_name or not last_name or not phone_number or not email or not message:
        return Response({'error': 'Please provide all the required fields'}, status=400)
    
    get_in_touch = GetInTouch()
    get_in_touch.first_name = first_name
    get_in_touch.last_name = last_name
    get_in_touch.phone_number = phone_number
    get_in_touch.email = email
    get_in_touch.emessageail = message
    get_in_touch.save()

    return Response({"data Updated successfully"}, status=status.HTTP_200_OK)


# @csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_data(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    image_url = ""
    if profile.image and hasattr(profile.image, 'url'):
        image_url = request.build_absolute_uri(profile.image.url)

    return Response({
        "email": user.email,
       "full_name": profile.full_name,
       "first_name": profile.first_name,
       "last_name": profile.last_name,
       "phone_number": profile.phone_number,
       "image": image_url

    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    image = request.FILES.get('image')

    # Get incoming data safely (fallback to old values)
    first_name = request.data.get('first_name', profile.first_name)
    last_name = request.data.get('last_name', profile.last_name)
    phone_number = request.data.get('phone_number', profile.phone_number)

    # Auto-generate full name
    full_name = f"{first_name} {last_name}".strip()

    # Save fields
    profile.first_name = first_name
    profile.last_name = last_name
    profile.phone_number = phone_number
    profile.full_name = full_name

    if image:
        profile.image = image

    profile.save()

    # Build absolute image URL
    image_url = (
        request.build_absolute_uri(profile.image.url)
        if profile.image and hasattr(profile.image, "url")
        else None
    )

    # Return UPDATED profile
    return Response(
        {
            "message": "Profile updated successfully",
            "email": user.email,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "full_name": profile.full_name,
            "phone_number": profile.phone_number,
            "image": image_url,
        },
        status=status.HTTP_200_OK,
    )



"""   
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MDg4MjQ3NCwiaWF0IjoxNzYwMDE4NDc0LCJqdGkiOiI5NTRlMDMyNDQ1ZWY0MDc2YWJlNTE0MDkxNjU3NWFiYSIsInVzZXJfaWQiOiIzIn0.0tGznhJwex06VnCAaeGCjF0nnxgcU3UPdZ30h8A7wtw",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwNzA5Njc0LCJpYXQiOjE3NjAwMTg0NzQsImp0aSI6ImQxZTEwNWRmZDFjZDQ0NTE5MjBkZmFjNjczMWE1ZTliIiwidXNlcl9pZCI6IjMifQ.BUNha-Eh665KTWkqVaE_jEsFhO1UEqZgvJw9ofAz0VA",

"""
