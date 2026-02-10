from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import jwt
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, LoginSerializer, RefreshSerializer
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data = request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh  = RefreshToken.for_user(user)
            
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=200)
    else:
        return Response(serializer.errors, status=400)
        

@api_view(['POST'])
def refresh(request):
    serializer = RefreshSerializer(data=request.data)
    if serializer.is_valid():
        refresh_token = serializer.validated_data['refresh_token']  
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access_token': str(refresh.access_token),
            }, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=401)
    else:
        return Response(serializer.errors, status=400)
    

@api_view(['POST'])
def logout(request):
    serializer = RefreshSerializer(data=request.data)
    if serializer.is_valid():
        # prefer body param, fall back to Authorization header
        refresh_token = serializer.validated_data.get('refresh_token')
        if not refresh_token:
            auth = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
            if auth and isinstance(auth, str) and auth.startswith('Bearer '):
                refresh_token = auth.split(' ', 1)[1].strip()

        if not refresh_token:
            return Response({'error': 'No refresh token provided'}, status=400)

        # decode payload without verifying signature to inspect token_type
        try:
            payload = jwt.decode(refresh_token, options={"verify_signature": False})
            token_type = payload.get('token_type')
        except Exception:
            return Response({'error': 'Token is malformed'}, status=400)

        if token_type != 'refresh':
            return Response({'error': 'Provided token is not a refresh token'}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully'}, status=200)
        except TokenError:
            return Response({'error': 'Refresh token is invalid or blacklisted'}, status=400)
        except InvalidToken:
            return Response({'error': 'Invalid or expired refresh token'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    else:
        return Response(serializer.errors, status=400)

class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        payload = request.data;
        serializer = UserSerializer(data=payload)
        isValid = serializer.is_valid()
        if isValid:
            serializer.save()
            return Response({'message': 'User created Successfully'}, status=201)
        else:
            return Response({'message': 'Invalid Form Data'}, status=422)
        


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            if user:
                serializer = UserSerializer(user)
                return Response(serializer.data)
            else:
                return Response({'message': 'User not found'}, status=404)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)
    
    def put(self, request, id):
            user = User.objects.get(id=id)
            if user:
                payload = request.data
                serializer = UserSerializer(user, data=payload)
                isValid = serializer.is_valid()
                if isValid:
                    serializer.save()
                    return Response({'message': 'User Updated Successfully'}, status=200)
                return Response()
            else:
                return Response({'message': 'User not found'}, status=404)
    
    def delete(self, request, id):
            user = User.objects.get(id=id)
            if user:
                user.delete()
                return Response({'message': 'User got deleted successfully'}, status=200)
            else:
                return Response({'message': 'User not found'}, status=404)