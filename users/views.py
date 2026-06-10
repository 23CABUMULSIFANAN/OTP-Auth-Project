import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    VerifyOTPSerializer,
    LoginSerializer,
    UserProfileSerializer
)
from .utils import send_otp_email, verify_otp
from .permissions import IsAdminRole, IsAdminOrUser

from rest_framework.permissions import IsAuthenticated

from rest_framework import status as status_code
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            thread = threading.Thread(target=send_otp_email, args=(user,))
            thread.daemon = True
            thread.start()
            return Response(
                {"message": "Registration successful. OTP sent to your email."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            success, message = verify_otp(user, otp_code)

            if success:
                user.is_verified = True
                user.save()
                tokens = get_tokens_for_user(user)
                return Response(
                    {"message": message, "tokens": tokens},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = authenticate(request, email=email, password=password)
            except Exception:
                return Response(
                    {"error": "Authentication error. Try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if user is None:
                return Response(
                    {"error": "Invalid email or password"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not user.is_verified:
                thread = threading.Thread(target=send_otp_email, args=(user,))
                thread.daemon = True
                thread.start()
                return Response(
                    {"error": "Account not verified. A new OTP has been sent to your email."},
                    status=status.HTTP_403_FORBIDDEN
                )

            tokens = get_tokens_for_user(user)
            return Response(
                {"message": "Login successful", "tokens": tokens},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class UserDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrUser]

    def get(self, request):
        if request.user.role == 'admin':
            # Admin sees all users
            users = CustomUser.objects.all().order_by('-created_at')
            serializer = UserProfileSerializer(users, many=True)
            return Response({
                "role": "admin",
                "total_users": users.count(),
                "users": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Normal user sees only their own profile
            serializer = UserProfileSerializer(request.user)
            return Response({
                "role": "user",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)


class PropertyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Both admin and user can view properties
        return Response({
            "message": "Properties fetched successfully",
            "role": request.user.role,
            "can_manage": request.user.role == 'admin'
        }, status=status.HTTP_200_OK)

    def post(self, request):
        # Only admin can add properties
        if request.user.role != 'admin':
            return Response(
                {"error": "You don't have permission to add properties. Admin access required."},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(
            {"message": "Property added successfully"},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        # Only admin can delete properties
        if request.user.role != 'admin':
            return Response(
                {"error": "You don't have permission to delete properties. Admin access required."},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(
            {"message": "Property deleted successfully"},
            status=status.HTTP_200_OK
        )


class AllUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        # Only admin can see all users
        users = CustomUser.objects.filter(role='user').order_by('-created_at')
        serializer = UserProfileSerializer(users, many=True)
        return Response({
            "total_users": users.count(),
            "users": serializer.data
        }, status=status.HTTP_200_OK)
    
    
from .models import SavedProperty

class SavePropertyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Save a property
        property_id = request.data.get('property_id')
        title = request.data.get('title')
        location = request.data.get('location')
        price = request.data.get('price')
        status = request.data.get('status')
        image = request.data.get('image')

        if SavedProperty.objects.filter(user=request.user, property_id=property_id).exists():
            return Response(
                {"message": "Already saved"},
                status=status_code.HTTP_200_OK
            )

        SavedProperty.objects.create(
            user=request.user,
            property_id=property_id,
            title=title,
            location=location,
            price=price,
            status=status,
            image=image
        )
        return Response(
            {"message": "Property saved successfully"},
            status=status_code.HTTP_201_CREATED
        )

    def delete(self, request):
        # Unsave a property
        property_id = request.data.get('property_id')
        SavedProperty.objects.filter(
            user=request.user,
            property_id=property_id
        ).delete()
        return Response(
            {"message": "Property removed from saved"},
            status=status_code.HTTP_200_OK
        )


class GetSavedPropertiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only returns THIS user's saved properties
        saved = SavedProperty.objects.filter(user=request.user).order_by('-saved_at')
        data = [{
            "property_id": s.property_id,
            "title": s.title,
            "location": s.location,
            "price": s.price,
            "status": s.status,
            "image": s.image,
            "saved_at": s.saved_at
        } for s in saved]
        return Response({"saved_properties": data}, status=status_code.HTTP_200_OK)