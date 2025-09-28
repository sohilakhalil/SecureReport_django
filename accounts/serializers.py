from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# -------------------------Serializer for Admin User Management----------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role', 'status', 'date_joined', 'password']
        extra_kwargs = {
            'email': {'required': False},
            'full_name': {'required': False},
            'role': {'required': False},
            'status': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# ----------------------Serializer for Current User Account----------------------
class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password', 'role', 'status']
        extra_kwargs = {
            'email': {'required': False},
            'full_name': {'required': False},
            'role': {'required': False},
            'status': {'required': False},
        }

# -------------------------JWT Login Serializer (using email)----------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

# --------------------------Password Reset Serializers-------------------------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
