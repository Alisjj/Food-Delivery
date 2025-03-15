import base64
import json
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from ..models import FoodItem


PASSWORD = 'pAssw0rd!' 

def create_user(username='user@example.com', password=PASSWORD): # new
    return get_user_model().objects.create_user(
        username=username,
        first_name='Test',
        last_name='User',
        delivery_location='123 Test St',
        delivery_latitude=40.7128,
        delivery_longitude=-74.0060,
        password=password
    )



class HttpMenuTest(APITestCase):
    def setUp(self):
        user = create_user()
        response = self.client.post(reverse('log_in'), data={
            'username': user.username,
            'password': PASSWORD,
        })
        self.access = response.data['access']

    
    def test_user_can_list_menu_items(self):
        menus = [
            FoodItem.objects.create(name='Spaghetti', price=10.00, category='main_course'),
            FoodItem.objects.create(name='Caesar Salad', price=8.00, category='appetizer'),
            FoodItem.objects.create(name='Tiramisu', price=6.00, category='dessert'),
        ]
        response = self.client.get(reverse('restaurants:menu_list'), HTTP_AUTHORIZATION=f'Bearer {self.access}')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
       

  
        