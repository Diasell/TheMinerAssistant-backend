# -*- coding: utf-8 -*-
#  import django services
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# import rest framework services
from rest_framework.authtoken.models import Token
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView


# import db models serializers
from mainApp.serializers.auth import (
    RegisterViewSerializer,
    AddChatIDSerializer,
    UserSerializer,
    LoginViewSerializer,
)


# import needed app models
from mainApp.models.userProfile import UserProfile

# import helper functions
from mainApp.utils.helperfunctions import (
    validate_user_registration,
    create_response_scelet
)


class RegisterAPIView(APIView):
    """
    API that allows users to register a new account.
    """
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser, JSONParser)
    serializer_class = RegisterViewSerializer

    def post(self, request, format=None):
        # get obligatory fields
        username = request.data["username"]
        password = request.data["password"]
        confirm_password = request.data["confirm_password"]
        phone_number = request.data["phone_number"]
        first_name = request.data["first_name"]
        try:
            photo = request.FILES['photo']
        except:
            photo = None

        user_input = validate_user_registration(username, password, confirm_password, photo)

        if user_input["is_valid"]:
            new_user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name
            )
            new_user.save()

            UserProfile(
                user=new_user,
                phone_number=phone_number,
                photo=photo
            ).save()

            token = Token.objects.get_or_create(user=new_user)[0]
            data = dict()
            data['Authorization'] = u"Token %s" % token
            data['BotLink'] = u"https://telegram.me/MinerAssistantBot"

            response = create_response_scelet(u'success', u"User has been created",  data)
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = create_response_scelet(u'failed', user_input["responseData"], {})
            return Response(response, status=status.HTTP_403_FORBIDDEN)


class AddChatIdView(APIView):
    """
    User passes his  telegram chat_id that he got from the chat bot after giving him his phone number
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AddChatIDSerializer

    def post(self, request):
        user = request.user
        chat_id = request.data['chat_id']

        if not user.userprofilemodel.is_verified:
            if chat_id == user.userprofilemodel.chat_id:
                user.userprofilemodel.is_verified = True
                user.userprofilemodel.save()
                user.save()

                token = Token.objects.get_or_create(user=user)[0]
                user_data = UserSerializer(user).data
                user_data["Authorization"] = u"Token %s" % token

                response = create_response_scelet(u'success', u"Welcome to Miner Assistant", user_data)
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_scelet(u'failure', u'Invalid code', {})
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        else:
            response = create_response_scelet(u'failure', u'Unauthorized action', {})
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class LoginAPIView(APIView):
    """
    API that allows users login and get unique Token.
    """
    #authentication_classes = (BasicAuthentication,)
    permission_classes = (AllowAny,)
    serializer_class = LoginViewSerializer

    def post(self, request):

        username = request.data["username"]
        password = request.data["password"]

        user = authenticate(username=username, password=password)

        if user:
            token = Token.objects.get_or_create(user=user)[0]
            data = UserSerializer(user).data
            data["Authorization"] = u"Token %s" % token
            response = create_response_scelet('success', 'Logged in successfully', data)
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = create_response_scelet('failed', 'User with such credentials not found', {})
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class OnLoginView(APIView):
    """
    User passes his  telegram chat_id that he got from the chat bot after giving him his phone number
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        if (request.user):
            user = request.user
            response_data = {
                'first_name': user.first_name,
                'avatar': None,
                'pools': []
            }
            if user.profile.photo:
                response_data['avatar'] = user.profile.photo.url
            pools = user.pool.all()
            if pools:
                for pool in pools:
                    response_data['pools'].append({
                        'name': pool.name,
                        'address': pool.address
                    })
                response = create_response_scelet(u"success", "success", response_data)
                return Response(response, status=status.HTTP_200_OK)

        else:
            response = create_response_scelet(u'failure', u'Unauthorized action', {})
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)