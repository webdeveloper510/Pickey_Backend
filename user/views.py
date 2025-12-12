import random
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer
from .models import User, PasswordResetOTP
from user.utils.email import send_verification_otp_email
from django.contrib.auth import authenticate


def api_response(code, message, data=None):
    """Unified API JSON response format."""
    return Response({
        "code": code,
        "message": message,
        "data": data
    }, status=code)


class SignupView(APIView):

    def send_phone_otp(self, phone):
        otp = random.randint(100000, 999999)
        # Integrate SMS provider here
        print(f"OTP sent to phone {phone}: {otp}")
        return otp

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            email = serializer.validated_data.get("email")
            phone = serializer.validated_data.get("phone_number")

            otp = random.randint(100000, 999999)
            expires_at = timezone.now() + timedelta(minutes=10)

            PasswordResetOTP.objects.create(
                user=user,
                otp=otp,
                expires_at=expires_at
            )

            if phone:
                self.send_phone_otp(phone)

            if email:
                send_verification_otp_email(
                    email=email,
                    otp=otp,
                    user_name=user.display_name or user.username
                )

            return api_response(
                200,
                "OTP sent successfully",
                {"user_id": user.id}
            )

        return api_response(400, "Validation failed", serializer.errors)


class VerifyOTPView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")

        try:
            otp_record = PasswordResetOTP.objects.filter(
                user_id=user_id,
                otp_verified=False
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            return api_response(400, "OTP not found")

        if timezone.now() > otp_record.expires_at:
            return api_response(400, "OTP expired")

        if str(otp_record.otp) != str(otp):
            return api_response(400, "Invalid OTP")

        otp_record.otp_verified = True
        otp_record.save()

        user = otp_record.user
        user.is_verified = True
        user.save()

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "display_name": user.display_name,
                "user_type": user.user_type
            },
            "tokens": {
                "access": access_token,
                "refresh": str(refresh)
            }
        }

        return api_response(200, "Account verified successfully", data)




def api_response(code, message, data=None):
    return Response({
        "code": code,
        "message": message,
        "data": data
    }, status=code)

class LoginView(APIView):

    def post(self, request):
        email_or_phone = request.data.get("email_or_phone")
        password = request.data.get("password")

        if not email_or_phone or not password:
            return api_response(400, "Email/Phone and Password are required")

        user = None

        # 🔍 If login with email
        if User.objects.filter(email=email_or_phone).exists():
            user_email = email_or_phone

        # 🔍 If login with phone
        else:
            try:
                user_obj = User.objects.get(phone_number=email_or_phone)
                user_email = user_obj.email   # authenticate needs email
            except User.DoesNotExist:
                return api_response(400, "Invalid email/phone or password")

        # 🔐 Authenticate user
        user = authenticate(email=user_email, password=password)

        if not user:
            return api_response(400, "Invalid email/phone or password")

        if not user.is_verified:
            return api_response(400, "Account not verified. Please verify OTP first.")

        # 🎟 Generate JWT
        refresh = RefreshToken.for_user(user)

        data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "username": user.username,
                "display_name": user.display_name,
                "user_type": user.user_type,
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }

        return api_response(200, "Login successful", data)
    
    

# class LoginView(APIView):

#     def post(self, request):
#         email_or_phone = request.data.get("email_or_phone")
#         password = request.data.get("password")
#         if not email_or_phone or not password:
#             return api_response(400, "Email/Phone and Password are required")
#         # 🔍 1. Try login by Email
#         user = User.objects.filter(email=email_or_phone).first()
#         # 🔍 2. If not found, try login by Phone Number
#         if not user:
#             user = User.objects.filter(phone_number=email_or_phone).first()
#         if not user:
#             return api_response(400, "Invalid email/phone or password")
#         # 🔐 Verify password
#         if not user.check_password(password):
#             return api_response(400, "Invalid email/phone or password")
#         # 🚫 Check verified or not
#         if not user.is_verified:
#             return api_response(400, "Account not verified. Please verify OTP first.")
#         # 🎟 Generate JWT
#         refresh = RefreshToken.for_user(user)
#         access = str(refresh.access_token)
#         refresh = str(refresh)
#         data = {
#             "user": {
#                 "id": user.id,
#                 "email": user.email,
#                 "phone_number": user.phone_number,
#                 "username": user.username,
#                 "display_name": user.display_name,
#                 "user_type": user.user_type,
#             },
#             "tokens": {
#                 "access": access,
#                 "refresh": refresh
#             }
#         }

#         return api_response(200, "Login successful", data)