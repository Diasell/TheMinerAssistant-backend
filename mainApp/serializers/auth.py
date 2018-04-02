from django.contrib.auth.models import User
from mainApp.models.userProfile import UserProfile
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name'
        )


class LoginViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )


class RegisterViewSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username')
    password = serializers.CharField(source='user.password')
    confirm_password = serializers.CharField(source='user.password')
    first_name = serializers.CharField(source='user.first_name')

    class Meta:
        model = UserProfile
        fields = (
            'username',
            'password',
            'confirm_password',
            'phone_number',
            'first_name',
            'photo',
        )


class AddChatIDSerializer(serializers.ModelSerializer):
    """
    Serializer for DRF DOCS for Add Chat ID Endpoint
    """
    chat_id = serializers.CharField(source='user_userprofile.chat_id')

    class Meta:
        model = Token
        fields = (
            'chat_id',
        )
