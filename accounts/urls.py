from django.urls import path
from .views import (
    UsersMinimalView, AccountView, MyTokenObtainPairView,
    PasswordResetRequestView, PasswordResetConfirmView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('users/', UsersMinimalView.as_view(), name='users-minimal'),
    path('users/<int:id>/', UsersMinimalView.as_view(), name='users-detail'),
    path('account/', AccountView.as_view(), name='account'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password_reset_confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
