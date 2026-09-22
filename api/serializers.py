from django.contrib.auth.models import User
from rest_framework import serializers
from notes.models import Note
from django.core.validators import RegexValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]{3,30}$',
    message=(
        'Username must be 3-30 characters long '
        'and contain only letters, numbers, and underscores.'
    )
)

password_validator = RegexValidator(
    regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
    message=(
        'Password must be at least 8 characters long '
        'and contain at least one uppercase letter, '
        'one lowercase letter, one number, '
        'and one special character.'
    )
)

class RegisterSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        validators=[username_validator]
    )

    email = serializers.EmailField(
        required=True
    )

    password = serializers.CharField(
        write_only=True,
        validators=[password_validator]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        return user

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Note
        fields=[
            'id',
            'title',
            'content',
            'image', 
            'created_at',
            'updated_at',
        ]
        read_only_fields=[
            'id',
            'created_at',
            'updated_at',
        ]

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message='OTP must be exactly 6 digits.'
            )
        ]
    )


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    new_password = serializers.CharField(
        write_only=True,
        validators=[password_validator]
)

class NotePaginationSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(
        allow_null=True
    )
    previous = serializers.URLField(
        allow_null=True
    )
    results = NoteSerializer(
        many=True
    )

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
