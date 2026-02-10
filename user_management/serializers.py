from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import jwt
from .models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(email = data['email'], password = data['password'])
        if user:
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError("Invalid credentials")
        
        
class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    def validate_refresh_token(self, value):
        # Only normalize the token here (strip optional 'Bearer ')
        if isinstance(value, str) and value.startswith('Bearer '):
            value = value.split(' ', 1)[1].strip()
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'