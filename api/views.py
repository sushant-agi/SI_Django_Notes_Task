from rest_framework import generics, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notes.models import Note

from .serializers import RegisterSerializer, NoteSerializer


class RegisterAPIView(generics.CreateAPIView):

    serializer_class = RegisterSerializer


class NoteViewSet(viewsets.ModelViewSet):

    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Note.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user
        )


class LogoutAPIView(generics.GenericAPIView):
    
    permission_classes = []

    def post(self, request):

        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=400
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Logout successful.'},
                status=200
            )

        except Exception:
            return Response(
                {'error': 'Invalid or expired refresh token.'},
                status=400
            )
