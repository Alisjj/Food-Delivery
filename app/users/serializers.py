from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model, password_validation
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        
        return value
    
    def validate_password1(self, value):
        password_validation.validate_password(value)
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('password2 must match password1')
        
        return data
    
    def create(self, validated_data):
        data = {
            key: value for key, value in validated_data.items()
            if key not in ('password1', 'password2')
        }

        data['password'] = validated_data['password1']

        data['verification_token'] = get_random_string(64)
        data['verification_token_expires'] = timezone.now() + timedelta(days=1)

        user = self.Meta.model.objects.create_user(**data)

        self._send_verification_email(user)


        return user
    
    def _send_verification_email(self, user):
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{user.verification_token}"
        subject = "Verify your email address"
        message = f"Please click the link to verify your email: {verification_url}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list)
    
    class Meta:
        model = get_user_model()
        fields = (
            'id', 'username', 'email','password1', 'password2', 'first_name', 'last_name',
            'delivery_location', 'delivery_latitude', 'delivery_longitude'
        )
        read_only_fields = ('id', 'email_verified')



class LoginSerializer(TokenObtainPairSerializer):
    # Override the validate method to check email verification
    def validate(self, attrs):
        # This calls the parent validate method which authenticates credentials
        data = super().validate(attrs)
        
        # Now check if the user is verified
        if not self.user.email_verified:
            raise serializers.ValidationError(
                {"detail": "Please verify your email address before logging in."}
            )
        
        # Add user data to the response
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'delivery_location': self.user.delivery_location,
            'delivery_latitude': self.user.delivery_latitude,
            'delivery_longitude': self.user.delivery_longitude
        }
            
        return data
    
    @classmethod
    def get_token(cls, user):
        # Get the token from the parent class
        token = super().get_token(user)
        
        # Add user data to the token payload
        token['username'] = user.username
        token['email'] = user.email
        token['email_verified'] = user.email_verified
        
        # Only include location data if available
        if user.delivery_location:
            token['delivery_location'] = user.delivery_location
            token['delivery_latitude'] = user.delivery_latitude
            token['delivery_longitude'] = user.delivery_longitude
        
        return token

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            user = get_user_model().objects.filter(verification_token=value).first()
            if not user:
                raise serializers.ValidationError('Invalid token')
            
            if user.verification_token_expires < timezone.now():
                raise serializers.ValidationError('Token expired')
            
            self.user = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid token')
    
    def save(self):
        self.user.email_verified = True
        self.user.verification_token = None
        self.user.verification_token_expires = None
        self.user.save()
        return self.user

class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.email_verified:
                raise serializers.ValidationError("This email is already verified.")
            self.user = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email address.")
    
    def save(self):
        # Generate new verification token
        self.user.verification_token = get_random_string(64)
        self.user.verification_token_expires = timezone.now() + timedelta(days=1)
        self.user.save()
        
        # Send verification email
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{self.user.verification_token}"
        subject = "Verify your email address"
        message = f"Please click the link to verify your email: {verification_url}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.user.email]
        
        send_mail(subject, message, from_email, recipient_list)
        return self.user    

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            return value
    
    def save(self):
        if hasattr(self, 'user'):
            token = get_random_string(64)
            self.user.verification_token = token
            self.user.verification_token_expires = timezone.now() + timedelta(hours=24)
            self.user.save()
            
            # Send password reset email
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
            subject = "Reset your password"
            message = f"Please click the link to reset your password: {reset_url}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [self.user.email]
            
            send_mail(subject, message, from_email, recipient_list)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            return value
    
    def save(self):
        if hasattr(self, 'user'):
            token = get_random_string(64)
            self.user.verification_token = token
            self.user.verification_token_expires = timezone.now() + timedelta(hours=24)
            self.user.save()
            
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
            subject = "Reset your password"
            message = f"Please click the link to reset your password: {reset_url}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [self.user.email]
            
            send_mail(subject, message, from_email, recipient_list)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate_token(self, value):
        try:
            user = User.objects.get(
                verification_token=value,
                verification_token_expires__gt=timezone.now()
            )
            self.user = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired password reset token.")
    
    def validate_new_password1(self, value):
        password_validation.validate_password(value)
        return value
    
    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords must match.'})
        return data
    
    def save(self):
        self.user.set_password(self.validated_data['new_password1'])
        self.user.verification_token = None
        self.user.verification_token_expires = None
        self.user.save()
        return self.user
