import uuid
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    busy_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def is_available(self):
        """Check if restaurant is currently available"""
        if self.busy_until is None:
            return True
        return timezone.now() >= self.busy_until

    def set_busy(self):
        self.busy_until = timezone.now() + timezone.timedelta(minutes=15)
        self.save()

    def set_available(self):
        self.busy_until = None
        self.save()

    @classmethod
    def find_nearest_available(cls, latitude, longitude):
        """Find nearest available restaurant based on coordinates"""
        # Get restaurants that are available (next_available_time is None or in the past)
        current_time = timezone.now()
        available_restaurants = cls.objects.filter(
            models.Q(busy_until__isnull=True) | 
            models.Q(busy_until__lte=current_time)
        )
        
        if not available_restaurants:
            return None
            
        # Simple distance calculation (not accurate for long distances)
        nearest = None
        min_distance = float('inf')
        
        for restaurant in available_restaurants:
            # Euclidean distance - not accurate for geographic coordinates
            # but sufficient for demonstration purposes
            distance = ((float(restaurant.latitude) - float(latitude)) ** 2 + 
                       (float(restaurant.longitude) - float(longitude)) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest = restaurant
                
        return nearest



class Courier(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='courier')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    # is_available = models.BooleanField(default=True)
    busy_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
     
    @property
    def is_available(self):
        """Check if courier is currently available"""
        if self.busy_until is None:
            return True
        return timezone.now() >= self.busy_until
    
    def set_busy(self):
        self.busy_until = timezone.now() + timezone.timedelta(minutes=15)
        self.save()

    def set_available(self):
        self.busy_until = None
        self.save()
    
    # def get_ab
    


class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('appetizer', 'Appetizer'),
        ('main_course', 'Main Course'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage'),
        ('side_dish', 'Side Dish'),
        ('breakfast', 'Breakfast'),
        ('special', 'Chef Special'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
    
    def get_absolute_url(self):
        return reverse('restaurants:menu_detail', kwargs={'item_id': self.id})
    
    class Meta:
        ordering = ['category', 'name']