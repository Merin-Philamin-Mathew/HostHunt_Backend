from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import OwnerSerializer
from .models import CustomPropertyOwner
import random
from django.core.mail import send_mail
from django.conf import settings
# from rest_framework_simplejwt.authentication import JWTAuthentication

    
class RegisterUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.get('values')  # Extract the 'values' dictionary
        print(data)

        # Check if the email already exists
        if CustomUser.objects.filter(email=data.get('email')).exists():
            return Response({'email': 'This email already exists.'})

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            # Generate OTP
            otp = random.randint(100000, 999999)
            self.send_otp(data['email'], otp) 

            registration_data = {
                'name': data['name'],
                'email': data['email'],
                'password': data['password'],
                'otp': otp  # Save OTP with registration data
            }

            return Response({'message': 'OTP sent to your email.','data':registration_data,}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def send_otp(self, email, otp):
        print(otp   )
        subject = 'Your OTP Code for Verification'
        message = f'Your OTP code is {otp}. Please use this to verify your email.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        # Send email
        send_mail(subject, message, email_from, recipient_list)


class VerifyOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        otp = request.data.get('otp')
        print(otp)
        registration_data = request.data['registered_data']
        print(registration_data)

        if  not registration_data:
            return Response({'error': 'No registration data found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if int(otp) == registration_data['otp']:
            print('2')
            user = CustomUser.objects.create_user(
                name=registration_data['name'],
                email=registration_data['email'],
                # password=registration_data['password'],
            )

            return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
        else:
            print('3')
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print('user/view/login')
        try:
            email = request.data['email']
            password = request.data['password']
            print(email,password)
        except KeyError:
            return Response({"error": "Not sufficient data"})
        print('received datas')
        user = CustomUser.objects.filter(email = email).first()
        print('user heii')

        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

        print('password correct')
        
        refresh = RefreshToken.for_user(user)
        print(refresh)
        refresh['email'] = str(user.email)
        user_profile = CustomUser.objects.get(email=email)
        serializer = UserSerializer(user_profile)

        content = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'isAuthenticated':user.is_active,
            "data":serializer.data
        }
        print('content')
        return Response(content, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("user/google-login")
        try:
            email = request.data['email']
            name = request.data['name']
            print(email,name)
        except KeyError:
            return Response({"error": "Not sufficient data"})
        
        user = CustomUser.objects.filter(email = email).first()
        print('uauau',user)
        if user is None:
            user = CustomUser.objects.create_user(
                name=name,
                email=email,
                password=''
            )
            print('new user by googleLogin',user)

        refresh = RefreshToken.for_user(user)
        print(refresh)
        refresh['email'] = str(user.email)
        user_profile = CustomUser.objects.get(email=email)
        serializer = UserSerializer(user_profile)

        content = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'isAuthenticated':user.is_active,
            "data":serializer.data
        }
        print('content',content)
        return Response(content, status=status.HTTP_200_OK)
        

        

