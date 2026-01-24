from django.urls import path
from . import views  # Import your views here

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_forgot_password_otp/', views.verify_forgot_password_otp, name='verify_forgot_password_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('change_password/', views.change_password, name='change_password'),
    path('social_signup_signup/', views.social_signup_signup, name='social_signup_signup'),
    path('get_in_touch/', views.get_in_touch, name='get_in_touch'),
    path('get_profile_data/', views.get_profile_data, name='get_profile_data'),
    path('update_profile/', views.update_profile, name='update_profile')

]
