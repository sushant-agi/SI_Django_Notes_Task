from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from notes.models import Note

from .serializers import RegisterSerializer, NoteSerializer, NotePaginationSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, VerifyOTPSerializer
from .serializers import CustomTokenObtainPairSerializer
from drf_spectacular.utils import ( OpenApiExample, OpenApiResponse, extend_schema, OpenApiParameter, OpenApiTypes) 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

import secrets

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail

from .redis_utils import is_rate_limited

from .pagination import NotePagination


class RegisterAPIView(APIView):

    permission_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterSerializer,
            400: OpenApiResponse(
                description='Invalid registration data.',
                response=dict,
                examples=[
                    OpenApiExample(
                        'Registration Error',
                        value={
                            'username': [
                                'A user with that username already exists.'
                            ]
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                'Registration Example',
                value={
                    'username': 'sushant',
                    'email': 'sushant@example.com',
                    'password': 'Test@12345'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Registration Response',
                value={
                    'Registration Successful'
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
    )

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class NoteListCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number.',
                required=False,
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of notes per page. Maximum: 20.',
                required=False,
            ),
        ],
        responses={
            200: NotePaginationSerializer,
        },
        examples=[
            OpenApiExample(
                'Notes List Response',
                value={
                    'count': 2,
                    'next': 'http://127.0.0.1:8000/api/notes/?page=2',
                    'previous': None,
                    'results': [
                        {
                            'id': 2,
                            'title': 'My First Note',
                            'content': 'This is my first note.',
                            'image': None,
                            'created_at': '2026-09-20T12:32:13Z',
                            'updated_at': '2026-09-20T12:32:13Z'
                        },
                        {
                            'id': 1,
                            'title': 'Another Note',
                            'content': 'This is another note.',
                            'image': None,
                            'created_at': '2026-09-19T10:00:00Z',
                            'updated_at': '2026-09-19T10:00:00Z'
                        }
                    ]
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )

    def get(self, request):

        cache_version_key = f"notes:version:user:{request.user.id}"

        version = cache.get(cache_version_key, 1)

        page_number = request.query_params.get("page", "1")
        page_size = request.query_params.get("page_size", "5")

        cache_key = (
            f"notes:user:{request.user.id}:"
            f"v:{version}:page:{page_number}:size:{page_size}"
)

        cached_notes = cache.get(cache_key)

        if cached_notes is not None:
            return Response(
                cached_notes,
                status=status.HTTP_200_OK
            )

        notes = Note.objects.filter(
            user=request.user
        ).order_by("-created_at")

        paginator = NotePagination()
        page = paginator.paginate_queryset(notes, request)

        serializer = NoteSerializer(
            page,
            many=True
        )

        response_data = paginator.get_paginated_response(serializer.data).data

        cache.set(
            cache_key,
            response_data,
            timeout=300
        )

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=NoteSerializer,
        responses={
            201: NoteSerializer,
            400: OpenApiResponse(
                description='Invalid registration data.',
                response=dict,
                examples=[
                    OpenApiExample(
                        'Registration Error',
                        value={
                            'username': [
                                'A user with that username already exists.'
                            ]
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                'Create Note Request',
                value={
                    'title': 'My First Note',
                    'content': 'This is my first note.'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Create Note Response',
                value={
                    'id': 1,
                    'title': 'My First Note',
                    'content': 'This is my first note.',
                    'image': None,
                    'created_at': '2026-09-20T10:00:00Z',
                    'updated_at': '2026-09-20T10:00:00Z'
                },
                response_only=True,
                status_codes=['201'],
            ),
        ],
    )

    def post(self, request):

        serializer = NoteSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save(
                user=request.user
            )

            cache_version_key = f"notes:version:user:{request.user.id}"

            version = cache.get(cache_version_key, 1)

            cache.set(
                cache_version_key,
                version + 1,
                timeout=None
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class NoteDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: NoteSerializer,
            404: dict,
        }
    )

    def get(self, request, pk):

        note = get_object_or_404(
            Note,
            pk=pk,
            user=request.user
        )

        serializer = NoteSerializer(note)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=NoteSerializer,
        responses={
            200: NoteSerializer,
            400: OpenApiResponse(
                    description='Invalid note data.',
                    response=dict,
                    examples=[
                        OpenApiExample(
                            'Validation Error',
                            value={
                                'title': [
                                    'This field is required.'
                                ]
                            },
                            response_only=True,
                        ),
                    ],
                ),
            404: OpenApiResponse(
                    description='Note not found or does not belong to the authenticated user.',
                    response=dict,
                    examples=[
                        OpenApiExample(
                            'Note Not Found',
                            value={
                                'detail': 'Not found.'
                            },
                            response_only=True,
                        ),
                    ],
                ),
        },
    )

    def put(self, request, pk):

        note = get_object_or_404(
            Note,
            pk=pk,
            user=request.user
        )

        serializer = NoteSerializer(
            note,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            cache_version_key = f"notes:version:user:{request.user.id}"

            version = cache.get(cache_version_key, 1)

            cache.set(
                cache_version_key,
                version + 1,
                timeout=None
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        request=NoteSerializer,
        responses={
            200: NoteSerializer,
            400: OpenApiResponse(
                    description='Invalid note data.',
                    response=dict,
                    examples=[
                        OpenApiExample(
                            'Validation Error',
                            value={
                                'title': [
                                    'This field is required.'
                                ]
                            },
                            response_only=True,
                        ),
                    ],
                ),
            404: OpenApiResponse(
                    description='Note not found or does not belong to the authenticated user.',
                    response=dict,
                    examples=[
                        OpenApiExample(
                            'Note Not Found',
                            value={
                                'detail': 'Not found.'
                            },
                            response_only=True,
                        ),
                    ],
                ),
        },

        examples=[
            OpenApiExample(
                'Update Note',
                value={
                    'title': 'Updated Note',
                    'content': 'Updated note content.'
                },
                request_only=True,
            ),
        ]
    )

    def patch(self, request, pk):

        note = get_object_or_404(
            Note,
            pk=pk,
            user=request.user
        )

        serializer = NoteSerializer(
            note,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            cache_version_key = f"notes:version:user:{request.user.id}"

            version = cache.get(cache_version_key, 1)

            cache.set(
                cache_version_key,
                version + 1,
                timeout=None
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        responses={
            200: NoteSerializer,
            404: OpenApiResponse(
                    description='Note not found or does not belong to the authenticated user.',
                    response=dict,
                    examples=[
                        OpenApiExample(
                            'Note Not Found',
                            value={
                                'detail': 'Not found.'
                            },
                            response_only=True,
                        ),
                    ],
                ),
        }
    )

    def delete(self, request, pk):

        note = get_object_or_404(
            Note,
            pk=pk,
            user=request.user
        )

        note.delete()

        cache_version_key = f"notes:version:user:{request.user.id}"

        version = cache.get(cache_version_key, 1)

        cache.set(
            cache_version_key,
            version + 1,
            timeout=None
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class LogoutAPIView(APIView):

    permission_classes = []

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh': {
                        'type': 'string'
                    }
                },
                'required': ['refresh'],
            }
        },
        responses={
            200: dict,
            400: OpenApiResponse(
                    description='Invalid or missing refresh token.',
                    response=dict,
                    examples=[
                        OpenApiExample(
                            'Missing Refresh Token',
                            value={
                                'error': 'Refresh token is required.'
                            },
                            response_only=True,
                        ),
                        OpenApiExample(
                            'Invalid Refresh Token',
                            value={
                                'error': 'Invalid or expired refresh token.'
                            },
                            response_only=True,
                        ),
                    ],
                ),
        },
        examples=[
            OpenApiExample(
                'Logout Request',
                value={
                    'refresh': 'your_refresh_token_here'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Logout Response',
                value={
                    'message': 'Logout successful.'
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )

    def post(self, request):

        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Logout successful.'},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {'error': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class ForgotPasswordAPIView(APIView):
    permission_classes = []

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description='OTP sent successfully.',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'message': 'OTP sent successfully.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid email or email not registered.',
                examples=[
                    OpenApiExample(
                        'Email not registered',
                        value={
                            'error': 'No account is registered with this email.'
                        }
                    )
                ]
            ),
        },
        description='Send a password-reset OTP to the registered email address.'
    )
    def post(self, request):

        client_ip = request.META.get(
            'REMOTE_ADDR',
            'unknown'
        )

        rate_limit_key = f"forgot_password_rate:{client_ip}"

        if is_rate_limited(
            rate_limit_key,
            limit=5,
            window=900
        ):
            return Response(
                {
                    'error': 'Too many password reset requests. Please try again later.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'No account is registered with this email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = str(secrets.randbelow(900000) + 100000)

        cache.set(
            f'password_reset_otp_{email}',
            otp,
            timeout=300
        )

        send_mail(
            subject='Password Reset OTP',
            message=(
                f'Your password reset OTP is: {otp}\n\n'
                'This OTP is valid for 5 minutes.'
            ),
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {'message': 'OTP sent successfully.'},
            status=status.HTTP_200_OK
        )

class VerifyOTPAPIView(APIView):
    permission_classes = []

    @extend_schema(
        request=VerifyOTPSerializer,
        responses={
            200: OpenApiResponse(
                description='OTP verified successfully.',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'message': 'OTP verified successfully.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid or expired OTP.',
                examples=[
                    OpenApiExample(
                        'Invalid OTP',
                        value={
                            'error': 'Invalid or expired OTP.'
                        }
                    )
                ]
            ),
        },
        description='Verify the OTP sent to the registered email address.'
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        cache_key = f'password_reset_otp_{email}'
        stored_otp = cache.get(cache_key)

        if stored_otp != otp:
            return Response(
                {'error': 'Invalid or expired OTP.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache.set(
            f'password_reset_verified_{email}',
            True,
            timeout=600
        )

        cache.delete(cache_key)

        return Response(
            {'message': 'OTP verified successfully.'},
            status=status.HTTP_200_OK
        )

class ResetPasswordAPIView(APIView):
    permission_classes = []

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description='Password reset successfully.',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'message': 'Password reset successfully.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='OTP verification required or invalid request.',
                examples=[
                    OpenApiExample(
                        'Not verified',
                        value={
                            'error': 'OTP verification required.'
                        }
                    )
                ]
            ),
        },
        description='Reset the password after successful OTP verification.'
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']

        verified_key = f'password_reset_verified_{email}'
        verified = cache.get(verified_key)

        if not verified:
            return Response(
                {'error': 'OTP verification required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        cache.delete(verified_key)

        return Response(
            {'message': 'Password reset successfully.'},
            status=status.HTTP_200_OK
        )

class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    'username': 'sushant',
                    'password': 'sushant@1234'
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
