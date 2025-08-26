from rest_framework import serializers
from .models import User, Role  

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'password']

class UserLoginSerializer(serializers.Serializer):  # New serializer for login
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)  # Password should not be read back
    role_id = serializers.IntegerField(required=True)
    # role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role')  # Link to Role model

# class OTPLoginSerializer(serializers.Serializer):
#     phone_number = serializers.CharField(max_length=15)
#     otp = serializers.CharField(max_length=6, required=False)
