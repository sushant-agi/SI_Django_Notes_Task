from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterAPIView, NoteViewSet, LogoutAPIView

router=DefaultRouter()
router.register(
    r'notes',
    NoteViewSet,
    basename='api_notes'
)

urlpatterns=[
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('', include(router.urls)),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
]