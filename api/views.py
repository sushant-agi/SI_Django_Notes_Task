from rest_framework import generics, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from notes.models import Note

from .serializers import RegisterSerializer, NoteSerializer

@extend_schema(
    responses={
        201: OpenApiResponse(
            response=RegisterSerializer,
            description='User registered successfully.'
        ),
        400: OpenApiResponse(
            description='Invalid registration data.'
        ),
    }
)

class RegisterAPIView(generics.CreateAPIView):

    serializer_class = RegisterSerializer

@extend_schema_view(
    list=extend_schema(
        responses={
            200: NoteSerializer,
            401: OpenApiResponse(
                description='Authentication credentials were not provided or are invalid.'
            ),
        }
    ),
    create=extend_schema(
        responses={
            201: NoteSerializer,
            400: OpenApiResponse(
                description='Invalid note data.'
            ),
            401: OpenApiResponse(
                description='Authentication credentials were not provided or are invalid.'
            ),
        }
    ),
    retrieve=extend_schema(
        responses={
            200: NoteSerializer,
            401: OpenApiResponse(
                description='Authentication credentials were not provided or are invalid.'
            ),
            404: OpenApiResponse(
                description='Note not found.'
            ),
        }
    ),
    update=extend_schema(
        responses={
            200: NoteSerializer,
            400: OpenApiResponse(
                description='Invalid note data.'
            ),
            401: OpenApiResponse(
                description='Authentication credentials were not provided or are invalid.'
            ),
            404: OpenApiResponse(
                description='Note not found.'
            ),
        }
    ),
    partial_update=extend_schema(
        responses={
            200: NoteSerializer,
            400: OpenApiResponse(
                description='Invalid note data.'
            ),
            401: OpenApiResponse(
                description='Authentication credentials were not provided or are invalid.'
            ),
            404: OpenApiResponse(
                description='Note not found.'
            ),
        }
    ),
    destroy=extend_schema(
        responses={
            204: OpenApiResponse(
                description='Note deleted successfully.'
            ),
            401: OpenApiResponse(
                description='Authentication credentials were not provided or are invalid.'
            ),
            404: OpenApiResponse(
                description='Note not found.'
            ),
        }
    ),
)


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
