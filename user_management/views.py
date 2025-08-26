from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import User, UserRole
from .serializers import UserLoginSerializer  
from All_information.models import Owner, Tenant
from rest_framework.views import APIView
from django.contrib.auth import logout
from rest_framework.authtoken.models import Token


# Login  Api View 
class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data.get('phone_number')
        password = serializer.validated_data.get('password')
        role_id = serializer.validated_data.get('role_id')

        if role_id == 3:
            # ✅ Login as Owner
            owner = Owner.objects.filter(owner_phone_number=phone_number).first()
            if owner and owner.password == password:
                return Response({
                    'message': 'Owner login successful',
                    'owner_id': owner.owner_id,
                    'owner_name': owner.owner_name,
                   
                }, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid Owner credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        elif role_id == 4:  # Tenant
            tenant = Tenant.objects.filter(tenant_phone_number=phone_number).first()

            if tenant and tenant.password == password:
                return Response({
                    'message': 'Tenant login success',
                    'tenant_id': tenant.tenant_id,
                    'tenant_name': tenant.tenant_name,
                }, status=status.HTTP_200_OK)

            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            # ✅ Default: regular User + UserRole
            try:
                user = User.objects.get(phone_number=phone_number)
                if user.check_password(password):
                    user_role_mapping = UserRole.objects.filter(user_id=user.id, role_id=role_id).first()
                    if user_role_mapping:
                        token, _ = Token.objects.get_or_create(user=user)
                        return Response({
                            'message': 'Login successful',
                            'token': token.key
                        }, status=status.HTTP_200_OK)
                    return Response({'message': 'Role mismatch. Login denied.'}, status=status.HTTP_403_FORBIDDEN)
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
# class LoginView(generics.GenericAPIView):
#     serializer_class = UserLoginSerializer

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         phone_number = serializer.validated_data.get('phone_number')
#         password = serializer.validated_data.get('password')
#         role_id = serializer.validated_data.get('role_id')

#         try:
#             user = User.objects.get(phone_number=phone_number)

#             if user.check_password(password):
#                 user_role_mapping = UserRole.objects.filter(user_id=user.id, role_id=role_id).first()
#                 if user_role_mapping:
#                     # ✅ Create or get token
#                     token, _ = Token.objects.get_or_create(user=user)

#                     return Response({
#                         'message': 'Login successful',
#                         'token': token.key
#                     }, status=status.HTTP_200_OK)

#                 return Response({'message': 'Role mismatch. Login denied.'}, status=status.HTTP_403_FORBIDDEN)

#             return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

#         except User.DoesNotExist:
#             return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)




# Logout API View
class LogoutView(APIView):
    def post(self, request):
        # Log the user out by ending their session
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)