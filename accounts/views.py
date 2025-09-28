from rest_framework import status, permissions, generics, mixins
from rest_framework.response import Response
from .models import CustomUser
from .serializers import (
    UserSerializer, AccountSerializer, MyTokenObtainPairSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

# ------------------ Custom Permissions ------------------
class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to Admin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'

class IsActiveUser(permissions.BasePermission):
    """
    Allows access only to active users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.status == 'active'

# ------------------ Admin User Management ------------------
class UsersMinimalView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    Admin-only API: list, create, update, delete users.
    Only active Admins can access.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsActiveUser, IsAdminUser]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# ------------------ Current User Account ----------------------------------------------------
class AccountView(generics.RetrieveUpdateAPIView):
    """
    API for the currently logged-in user to view/update their account.
    Only active users can access.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsActiveUser]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs, partial=True)

# ------------------ JWT Login View ----------------------------------------------------------------
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Login API using email + password.
    """
    serializer_class = MyTokenObtainPairSerializer

# ------------------ Password Reset Request -------------------------------------------------------
class PasswordResetRequestView(generics.GenericAPIView):
    """
    Request password reset via email.
    Active status not required.
    """
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Email found. Proceed to reset password."}, status=status.HTTP_200_OK)

# ------------------ Password Reset Confirm --------------------------------------------------
class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm password reset.
    Active status not required.
    """
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']

        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Invalid email"}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
