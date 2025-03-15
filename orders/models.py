import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, Courier


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('DELIVERING', 'Delivering'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, related_name='orders')
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Set estimated delivery time to 15 minutes after order creation
        if not self.estimated_delivery_time and self.status == 'PENDING':
            self.estimated_delivery_time = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def assign_restaurant_and_courier(self, latitude, longitude):
        # Find nearest available restaurant
        restaurant = Restaurant.find_nearest_available(
            latitude, 
            longitude
        )
        
        if not restaurant:
            return False
        
        # Get associated courier
        courier = restaurant.courier
        
        if not courier or not courier.is_available:
            return False
        
        # Assign restaurant and courier
        self.restaurant = restaurant
        self.courier = courier
        self.status = 'PREPARING'
        self.save()
        
        # Mark restaurant and courier as busy
        restaurant.set_busy()
        courier.set_busy()
        
        return True
    

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey('restaurants.FoodItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.food_item.name} in Order #{self.order.id}"
    

    def subtotal(self):
        return self.quantity * self.price

