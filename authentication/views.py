from django.shortcuts import render
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomOwner, CustomUser, UserProfile, IdentityVerification 
from .seriallizers import OwnerSerializer, UserSerializer, AdminUserSerializer, ProfilePicSerializer, UserProfileSerializer

import random
from django.conf import settings
    
from rest_framework_simplejwt.views import TokenObtainPairView

from .tasks import send_email_task

from property.utils import Upload_to_s3, delete_file_from_s3,delete_file_from_s3_by_url
from .seriallizers import IdentityVerificationSerializer

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
# class CustomOwnerTokenView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         owner = CustomOwner.objects.filter(email=request.data['email']).first()
#         if owner and owner.check_password(request.data['password']):
#             # Issue token for owner
#             return super().post(request, *args, **kwargs)
#         return Response({'error': 'Invalid credentials'}, status=401)

# class CustomOwnerRefreshToken(RefreshToken):
#     @classmethod
#     def for_owner(cls, owner):
#         token = cls()
#         return token

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

        print(model, serializer, "..........................")
        if model.objects.filter(email=data.get('email')).exists():
            return Response({'email': 'This email already exists.'})

        if serializer.is_valid():
            # Generate OTP
            otp = random.randint(100000, 999999)
            self.send_otp(data['email'], otp)

            print('otp set going to register')
            registration_data = {
                'name': data['name'],
                'email': data['email'],
                'password': data['password'],
            }

            request.session['otp'] = otp
            getotp = request.session.get('otp')
            print(getotp)

            return Response({'message': 'OTP sent to your email.', 'data': registration_data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_otp(self, email, otp):
        subject = 'Your OTP Code for Verification'
        message = f'Your OTP code is {otp}. Please use this to verify your email.'
        recipient_list = [email]

        # Send email using Celery task
        send_email_task.delay(subject, message, recipient_list)


class VerifyOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
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
                model = CustomUser
            else:
                print('registering the user')
                model = CustomOwner

            user = model.objects.create_user(
            name=registration_data['name'],
            email=registration_data['email'],
            password=registration_data['password'],
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
            print(request.data)
            email = request.data['email']
            password = request.data['password']
            user_type = request.data['user_type']
        except KeyError:
            return Response({"error": "Not sufficient data"})
        print('received datas')
        
        if user_type == 'user':
            model, serializer, role = CustomUser, UserSerializer, 'user'
        elif user_type == 'admin':
            model,serializer,role = CustomUser, AdminUserSerializer, 'admin'
        else:
            model, serializer, role = CustomOwner, OwnerSerializer, 'owner'

        user = model.objects.filter(email = email).first()
        print('user heii',user)

        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user_type == 'admin' and not user.is_superuser:
            return Response({"error": "User is not an admin. Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # if user_type == 'user':
        #     refresh = RefreshToken.for_user(user)
        #     print('user_type == user') 
        # else:
        #     refresh = CustomOwnerRefreshToken.for_owner(user)
        #     print('user_type = owner')

        # Generate tokens
          # Prepare additional details
        profile_data = None
        identity_verification_data = None

        try:
            profile = UserProfile.objects.get(user=user)
            profile_data = {
                'profile_pic': profile.profile_pic if profile.profile_pic else None,
                'phone_number': profile.phone_number,
                'date_of_birth': profile.date_of_birth,
                'gender': profile.gender,
                'about_me': profile.about_me,
                'address': profile.address
            }
        except UserProfile.DoesNotExist:
            profile_data = None

        try:
            identity_verification = user.identity_verification
            identity_verification_data = {
                'identity_card': identity_verification.identity_card,
                'identity_proof_number': identity_verification.identity_proof_number,
                'identity_card_front_img_url': identity_verification.identity_card_front_img_url,
                'identity_card_back_img_url': identity_verification.identity_card_back_img_url,
                'status': identity_verification.status
            }
        except IdentityVerification.DoesNotExist:
            identity_verification_data = None

        refresh = RefreshToken.for_user(user)
        refresh['role'] = role
        refresh['email'] = str(user.email)
        refresh['id'] = str(user.id)
        serializer = serializer(user)

        response = Response({
            'access': str(refresh.access_token),
            'profile_pic': profile_data.get('profile_pic') if profile_data else None,
            'profile': profile_data,
            'identity_verification': identity_verification_data,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,  # Use True in production
            samesite='Lax',  # Adjust as needed (Lax, Strict, or None for cross-site requests)
            max_age=7 * 24 * 60 * 60  # 7 days in seconds
        )
        return response
    


class CustomTokenRefreshView(TokenRefreshView):
    print('custom refresh view')
    def post(self, request, *args, **kwargs):
        print('custom refresh viewooo')
        refresh_token = request.COOKIES.get('refresh_token')
        print('refresh_token',refresh_token, request.data)
        if not refresh_token:
            return Response({"error": "Refresh token missing in cookies"}, status=400)
        request.data['refresh'] = refresh_token
        return super().post(request, *args, **kwargs)


    
class ForgotPassword(APIView):
    def post(self, request):
        pass

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
                password='123123'
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
    
    

class UploadIdentityVerification(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print('identity-verification',request.data)
        data = request.data.copy()
        
        data['user'] = request.user.id

        front_img = request.FILES.get('identity_card_front_img')
        back_img = request.FILES.get('identity_card_back_img')

        if not front_img or not back_img:
            return Response(
                {'error': 'Both front and back images are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            s3_front_path = f"identity_verification/{request.user.id}/front/"
            front_img_url = Upload_to_s3(front_img, s3_front_path)
            data['identity_card_front_img_url'] = front_img_url

            s3_back_path = f"identity_verification/{request.user.id}/back/"
            back_img_url = Upload_to_s3(back_img, s3_back_path)
            data['identity_card_back_img_url'] = back_img_url
            data['status'] = 'in_review'

        except Exception as e:
            return Response(
                {'error': f'Image upload failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        print('files uploaded in the s3 bucket')

        serializer = IdentityVerificationSerializer(data=data)
        print('serializer',serializer)
        if serializer.is_valid():
            try:
                print('saving the identity verification')
                identity_verification = serializer.save()
                return Response({
                    'message': 'Profile Picture submitted successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                print('===============\nError while saving identity verification:', {str(e)})
                delete_file_from_s3(s3_front_path, front_img.name)
                delete_file_from_s3(s3_back_path, back_img.name)
                return Response(
                    {'error': f'Submission failed: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        print('===============\nError while saving identity verification:', serializer.errors)
        delete_file_from_s3(s3_front_path, front_img.name)
        delete_file_from_s3(s3_back_path, back_img.name)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UploadProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print('pro_pic',request.data)
        data = request.data
        data['user'] = request.user.id
        pro_pic = request.FILES.get('pro_pic')

        if not pro_pic :
            return Response(
                {'error': 'Profile picture is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            s3_front_path = f"pro_pic/{request.user.id}/"
            pro_pic_url = Upload_to_s3(pro_pic, s3_front_path)
            data['profile_pic'] = pro_pic_url


        except Exception as e:
            return Response(
                {'error': f'Image upload failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        print('files uploaded in the s3 bucket')

        serializer = ProfilePicSerializer(data=data)
        print('serializer',serializer)
        if serializer.is_valid():
            try:
                print('saving the identity verification')
                propic = serializer.save()
                return Response({
                    'message': 'Profile Picture submitted successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                print('===============\nError while saving pro pic:', {str(e)})
                delete_file_from_s3(s3_front_path, pro_pic.name)
                return Response(
                    {'error': f'Submission failed: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        print('===============\nError while saving pro pic:', serializer.errors)
        delete_file_from_s3(s3_front_path, pro_pic.name)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        new_pro_pic = request.FILES.get('pro_pic')
        
        if not new_pro_pic:
            return Response(
                {'error': 'Profile picture is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            
            old_pro_pic = user_profile.profile_pic
            
            s3_front_path = f"pro_pic/{request.user.id}/"
            pro_pic_url = Upload_to_s3(new_pro_pic, s3_front_path)
            
            data = {
                'user': request.user.id,
                'profile_pic': pro_pic_url
            }
            
            serializer = ProfilePicSerializer(user_profile, data=data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                if old_pro_pic:
                    try:
                        delete_file_from_s3_by_url(old_pro_pic)
                    except Exception as delete_error:
                        print(f"Error deleting old profile picture: {delete_error}")
                
                return Response({
                    'message': 'Profile Picture submitted successfully',
                    'data': serializer.data  # Exactly same as POST response
                }, status=status.HTTP_201_CREATED)
            
            delete_file_from_s3(s3_front_path, new_pro_pic.name)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            try:
                delete_file_from_s3(s3_front_path, new_pro_pic.name)
            except:
                pass
            
            return Response(
                {'error': f'Submission failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retrieve or create profile for the current user
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

