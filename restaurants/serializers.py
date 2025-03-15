from rest_framework import serializers
from .models import Restaurant, Courier, FoodItem 




class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            'id', 'name', 'address', 'latitude', 'longitude', 
            'is_active', 'busy_until', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')



class MenuItemSerializer(serializers.ModelSerializer):
    # category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = FoodItem
        fields = (
            'id', 'name', 'description', 'price', 'image_url', 
            'category', 'is_available', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')