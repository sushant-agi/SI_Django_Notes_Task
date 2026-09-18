from django.contrib.auth.models import User
from rest_framework import serializers
from notes.models import Note

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['username', 'password']
    
    def create(self, validated_data):
        user=User.objects.create_user(
            username=validated_data['username'],
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