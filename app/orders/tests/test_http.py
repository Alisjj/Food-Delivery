# tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import  Restaurant, Order
from restaurants.models import FoodItem, Courier
from django.utils import timezone
import json

User = get_user_model()

class OrderFlowTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            delivery_location='123 Test St',
            delivery_latitude=40.7128,
            delivery_longitude=-74.0060,
            email='test@example.com',
            password='testpassword'
        )
        
        # Create an admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        
        # Create test food items
        self.pizza = FoodItem.objects.create(
            name='Pizza',
            description='Delicious pizza',
            price=10.99,
            category='Italian'
        )
        
        self.burger = FoodItem.objects.create(
            name='Burger',
            description='Juicy burger',
            price=8.99,
            category='American'
        )
        
        # Create a test restaurant
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            address='123 Test St',
            latitude=40.7128,
            longitude=-74.0060,
            # is_available=True
        )
        
        # Create a courier for the restaurant
        self.courier = Courier.objects.create(
            name='Test Courier',
            restaurant=self.restaurant,
            # is_available=True
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_list_food_items(self):
        """Test listing food items"""
        self.client.force_authenticate(user=self.user)
        url = reverse('restaurants:menu_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_place_order(self):
        """Test placing an order"""
        self.client.force_authenticate(user=self.user)
        url = reverse('orders:order-list')
        
        # Create order data
        order_data = {
            'items': [
                {'food_item_id': self.pizza.id, 'quantity': 2},
                {'food_item_id': self.burger.id, 'quantity': 1}
            ]
        }
        
        response = self.client.post(url, data=json.dumps(order_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check order was created correctly
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.restaurant, self.restaurant)
        self.assertEqual(order.courier, self.courier)
        self.assertEqual(order.status, 'PREPARING')
        self.assertEqual(order.items.count(), 2)
        
        # Check restaurant and courier are now busy
        self.restaurant.refresh_from_db()
        self.courier.refresh_from_db()
        self.assertFalse(self.restaurant.is_available)
        self.assertFalse(self.courier.is_available)
    
    def test_order_without_available_restaurant(self):
        """Test placing an order when no restaurants are available"""
        # Mark restaurant as unavailable
        # self.restaurant.is_available = False
        self.restaurant.busy_until = timezone.now() + timezone.timedelta(minutes=15)
        self.restaurant.save()
        
        self.client.force_authenticate(user=self.user)
        url = reverse('orders:order-list')
        
        # Create order data
        order_data = {
            'items': [
                {'food_item_id': self.pizza.id, 'quantity': 2},
            ]
        }
        
        response = self.client.post(url, data=json.dumps(order_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_order(self):
        """Test cancelling an order"""
        # Create an order first
        order = Order.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            courier=self.courier,
            status='PREPARING',
            total_price=20.97,
            estimated_delivery_time=timezone.now() + timezone.timedelta(minutes=15)
        )
        
        # Make restaurant and courier busy
        self.restaurant.set_busy()
        self.courier.set_busy()
        
        self.client.force_authenticate(user=self.user)
        url = reverse('orders:order-cancel', kwargs={'pk': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check order was cancelled
        order.refresh_from_db()
        self.assertEqual(order.status, 'CANCELLED')
        
        # Check restaurant and courier are available again
        self.restaurant.refresh_from_db()
        self.courier.refresh_from_db()
        self.assertTrue(self.restaurant.is_available)
        self.assertTrue(self.courier.is_available)

    def test_nearest_restaurant(self):
        """Test finding the nearest restaurant"""
        # Create another restaurant
        Restaurant.objects.create(
            name='Second Restaurant',
            address='456 Test St',
            latitude=40.7128,
            longitude=-74.0060,
        )
        
        # Check the nearest restaurant
        nearest = Restaurant.find_nearest_available(self.user.delivery_latitude, self.user.delivery_longitude)
        self.assertEqual(nearest, self.restaurant)
    
    

        