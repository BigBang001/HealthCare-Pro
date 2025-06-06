from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from .serializers import UserSerializer
import logging
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken

def index(request):
    return render(request, 'index.html')

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    if not all(k in data for k in ('name', 'email', 'password')):
        return Response({
            'error': 'Missing required fields',
            'message': 'Name, email, and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    name = data['name'].strip()
    email = data['email'].strip().lower()
    password = data['password']

    if len(name) < 2:
        return Response({
            'error': 'Invalid name',
            'message': 'Name must be at least 2 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 6:
        return Response({
            'error': 'Invalid password',
            'message': 'Password must be at least 6 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)

    if '@' not in email or '.' not in email:
        return Response({
            'error': 'Invalid email',
            'message': 'Please provide a valid email address'
        }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'Email already exists',
            'message': 'A user with this email already exists'
        }, status=status.HTTP_409_CONFLICT)

    user = User.objects.create(
        username=email,
        email=email,
        first_name=name,
        password=make_password(password)
    )

    refresh = RefreshToken.for_user(user)
    logger.info(f"New user registered: {email}")

    return Response({
        'message': 'User registered successfully',
        'user': UserSerializer(user).data,
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data
    if not all(k in data for k in ('email', 'password')):
        return Response({
            'error': 'Missing credentials',
            'message': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    email = data['email'].strip().lower()
    password = data['password']

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid credentials',
            'message': 'Invalid email or password'
        }, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, user.password):
        return Response({
            'error': 'Invalid credentials',
            'message': 'Invalid email or password'
        }, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    logger.info(f"User logged in: {email}")

    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    return Response({
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)
