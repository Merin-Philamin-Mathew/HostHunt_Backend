from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomOwner, CustomUser
from .seriallizers import OwnerSerializer, UserSerializer

import random
from django.conf import settings
from django.core.mail import send_mail

# Create your views here.
class RegisterUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print('authentication/register')
        data = request.data  # Extract the 'values' dictionary
        print(data)

        if data['user_type'] == 'property_owner':
            model = CustomOwner
            serializer = OwnerSerializer(data=data)
        elif data['user_type'] == 'user':
            model = CustomUser
            serializer = UserSerializer(data=data)

        print(model,serializer,"..........................")
        if model.objects.filter(email=data.get('email')).exists():
            return Response({'email': 'This email already exists.'})

       
        if serializer.is_valid():
            # Generate OTP
            otp = random.randint(100000, 999999)
            self.send_otp(data['email'], otp) 

            registration_data = {
                'name': data['name'],
                'email': data['email'],
                'password': data['password'],
            }

            request.session['otp'] = otp
            getotp = request.session.get('otp')
            print(getotp)

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
        print("jjjjjjjjjjjjjjj",request.headers)
        print('authentication/otp')
        otp = request.data.get('otp')
        user_type = request.data.get('user_type')
        print('otp',otp)
        registration_data = request.data['registered_data']
        print('registration_data',registration_data)


        getotp = request.session.get('otp')
        print('/verifyOtp getotp', getotp)

    
        if  not registration_data:
            return Response({'error': 'No registration data found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if getotp == int(otp):
            print('2')
            if user_type == 'user':
                print('ksdfhnsdkl')
                model = CustomUser
            else:
                print("dfsdfsdfdsfsdfd///////////")
                model = CustomOwner

        

            user = model.objects.create_user(
                name=registration_data['name'],
                email=registration_data['email'],
                password=registration_data['password'],
            )

            print(model,'.......................................')

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
            user_type = request.data['user_type']
            print(email,password, user_type)
        except KeyError:
            return Response({"error": "Not sufficient data"})
        print('received datas')
        if user_type == 'user':
            model, serializer = CustomUser, UserSerializer
        else:
            model, serializer = CustomOwner, OwnerSerializer

        user = model.objects.filter(email = email).first()
        print('user heii',user)

        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

        print('password correct')
        
          # Handle RefreshToken generation based on user type
        if isinstance(user, CustomUser):
            refresh = RefreshToken.for_user(user)
            refresh['role'] = 'user'
        else:
            # Manually create a token for CustomOwner
            refresh = RefreshToken()
            refresh['role'] = 'owner'
            refresh['email'] = str(user.email)
            # Add custom owner-related fields if needed
            
        print(refresh)
        refresh['email'] = str(user.email)
        user_profile = model.objects.get(email=email)
        serializer = serializer(user_profile)

        content = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            # 'isAuthenticated':user.is_active,
            "data":serializer.data
        }
        print('content',content)
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
        

