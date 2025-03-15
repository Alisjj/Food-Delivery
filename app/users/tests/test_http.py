# tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json
from django.utils import timezone
from datetime import timedelta
from django.core import mail

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('users:signup')
        self.login_url = reverse('users:login')
        self.email_verify_url = reverse('users:verify-email')
        self.password_reset_url = reverse('users:password-reset')
        self.password_reset_confirm_url = reverse('users:password-reset-confirm')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
        }
        
        self.verified_user = User.objects.create_user(
            username='verifieduser',
            email='verified@example.com',
            password='AnotherStrong123!',
            email_verified=True
        )

    def test_user_signup(self):
        """Test user signup process"""
        response = self.client.post(self.signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        
        self.assertFalse(user.email_verified)
        self.assertIsNotNone(user.verification_token)
        self.assertIsNotNone(user.verification_token_expires)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Verify your email address')
        self.assertIn(user.verification_token, mail.outbox[0].body)

    def test_signup_password_mismatch(self):
        """Test signup with mismatched passwords"""
        data = self.user_data.copy()
        data['password2'] = 'DifferentPassword123!'
        
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_weak_password(self):
        """Test signup with weak password"""
        data = self.user_data.copy()
        data['password1'] = data['password2'] = 'password'
        
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password1', response.data)

    def test_signup_existing_email(self):
        """Test signup with already registered email"""
        # First user
        self.client.post(self.signup_url, self.user_data, format='json')
        
        data = self.user_data.copy()
        data['username'] = 'another_user'
        
        response = self.client.post(self.signup_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_verified_user(self):
        """Test login process for verified user"""
        response = self.client.post(self.login_url, {
            'username': 'verifieduser',
            'password': 'AnotherStrong123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_credentials(self):
        """Test login with wrong credentials"""
        response = self.client.post(self.login_url, {
            'username': 'verifieduser',
            'password': 'WrongPassword123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_verification(self):
        """Test email verification process"""
        user = User.objects.create_user(
            username='unverifieduser',
            email='unverified@example.com',
            password='StrongPassword123!',
            email_verified=False,
            verification_token='valid_token',
            verification_token_expires=timezone.now() + timedelta(days=1)
        )
        
        response = self.client.post(self.email_verify_url, {
            'token': 'valid_token'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertIsNone(user.verification_token)
        self.assertIsNone(user.verification_token_expires)

    def test_email_verification_expired_token(self):
        """Test email verification with expired token"""
        User.objects.create_user(
            username='expireduser',
            email='expired@example.com',
            password='StrongPassword123!',
            email_verified=False,
            verification_token='expired_token',
            verification_token_expires=timezone.now() - timedelta(days=1)
        )
        
        response = self.client.post(self.email_verify_url, {
            'token': 'expired_token'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request(self):
        """Test password reset request process"""
        response = self.client.post(self.password_reset_url, {
            'email': 'verified@example.com'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Reset your password')
        
        user = User.objects.get(email='verified@example.com')
        self.assertIsNotNone(user.verification_token)
        self.assertIsNotNone(user.verification_token_expires)

    def test_password_reset_request_nonexistent_email(self):
        """Test password reset request with nonexistent email"""
        response = self.client.post(self.password_reset_url, {
            'email': 'nonexistent@example.com'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm(self):
        """Test password reset confirmation process"""
        user = User.objects.create_user(
            username='resetuser',
            email='reset@example.com',
            password='OldPassword123!',
            verification_token='reset_token',
            verification_token_expires=timezone.now() + timedelta(days=1)
        )
        
        response = self.client.post(self.password_reset_confirm_url, {
            'token': 'reset_token',
            'new_password1': 'NewPassword456!',
            'new_password2': 'NewPassword456!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user.refresh_from_db()
        self.assertIsNone(user.verification_token)
        self.assertIsNone(user.verification_token_expires)
        
        self.assertTrue(self.client.login(username='resetuser', password='NewPassword456!'))
        self.assertFalse(self.client.login(username='resetuser', password='OldPassword123!'))

    def test_password_reset_confirm_mismatch(self):
        """Test password reset confirm with mismatched passwords"""
        User.objects.create_user(
            username='mismatchuser',
            email='mismatch@example.com',
            password='OldPassword123!',
            verification_token='mismatch_token',
            verification_token_expires=timezone.now() + timedelta(days=1)
        )
        
        response = self.client.post(self.password_reset_confirm_url, {
            'token': 'mismatch_token',
            'new_password1': 'NewPassword456!',
            'new_password2': 'DifferentPassword789!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password2', response.data)


class JWTTokenTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('users:login')
        
        self.verified_user = User.objects.create_user(
            username='verified',
            email='verified@example.com',
            password='StrongPassword123!',
            email_verified=True,
            first_name='Verified',
            last_name='User',
            delivery_location='123 Test St',
            delivery_latitude=12.34,
            delivery_longitude=56.78
        )
        
        self.unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='StrongPassword123!',
            email_verified=False
        )

    def test_jwt_payload_verified_user(self):
        """Test JWT payload for verified user"""
        response = self.client.post(self.login_url, {
            'username': 'verified',
            'password': 'StrongPassword123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        import jwt
        from django.conf import settings
        
        token = response.data['access']
       
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            
            self.assertEqual(payload['username'], 'verified')
            self.assertEqual(payload['email'], 'verified@example.com')
            self.assertTrue(payload['email_verified'])
            self.assertEqual(payload['delivery_location'], '123 Test St')
            self.assertEqual(payload['delivery_latitude'], 12.34)
            self.assertEqual(payload['delivery_longitude'], 56.78)
            
        except jwt.PyJWTError:
            self.fail("JWT decode error")

    def test_jwt_payload_unverified_user(self):
        """Test JWT payload for unverified user"""
        response = self.client.post(self.login_url, {
            'username': 'unverified',
            'password': 'StrongPassword123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        import jwt
        
        token = response.data['access']
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check user data in token
            self.assertEqual(payload['username'], 'unverified')
            self.assertEqual(payload['email'], 'unverified@example.com')
            self.assertFalse(payload['email_verified'])
            self.assertNotIn('delivery_location', payload)
            
        except jwt.PyJWTError:
            self.fail("JWT decode error")