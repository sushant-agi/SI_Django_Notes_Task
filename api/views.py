from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

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
