from django.urls import path

from .views import (
    RegisterAPIView,
    NoteListCreateAPIView,
    NoteDetailAPIView,
    LogoutAPIView,
    ForgotPasswordAPIView,
    VerifyOTPAPIView,
    ResetPasswordAPIView,
)


urlpatterns = [
    path(
        'register/',
        RegisterAPIView.as_view(),
        name='api_register'
    ),

    path(
        'logout/',
        LogoutAPIView.as_view(),
        name='api_logout'
    ),

    path(
        'notes/',
        NoteListCreateAPIView.as_view(),
        name='api_notes'
    ),

    path(
        'notes/<int:pk>/',
        NoteDetailAPIView.as_view(),
        name='api_note_detail'
    ),

    path(
        'forgot-password/',
        ForgotPasswordAPIView.as_view(),
        name='api_forgot_password'
    ),

    path(
        'verify-otp/',
        VerifyOTPAPIView.as_view(),
        name='verify_otp'
    ),
    path(
        'reset-password/',
        ResetPasswordAPIView.as_view(),
        name='api_reset_password'
    ),
]
