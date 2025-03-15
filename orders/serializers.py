from rest_framework import serializers
from .models import Order, OrderItem
from restaurants.models import FoodItem
from django.db import transaction


class OrderItemSerializer(serializers.ModelSerializer):
    food_item = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'quantity', 'price', 'subtotal']
        read_only_fields = ['price', 'subtotal']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    food_item_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ['food_item_id', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    courier_name = serializers.CharField(source='courier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'restaurant', 'restaurant_name', 
                  'courier', 'courier_name', 'status', 'status_display', 'total_price', 
                'order_time','estimated_delivery_time', 
                   'items']
        read_only_fields = ['id', 'user', 'restaurant', 'courier', 'status', 'total_price', 'order_time', 'estimated_delivery_time']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)
    # delivery_address = serializers.CharField(required=True)
    # delivery_latitude = serializers.FloatField(required=True)
    # delivery_longitude = serializers.FloatField(required=True)

    class Meta:
        model = Order
        fields = ['items']

    def validate_items(self, items):
        if not items or len(items) == 0:
            raise serializers.ValidationError("Order must have at least one item")
        
        food_ids = [item['food_item_id'] for item in items]
        food_items = FoodItem.objects.filter(id__in=food_ids)

        if len(food_ids) != len(food_items):
            raise serializers.ValidationError("One or more menu items do not exist")
        
        return items
    
    @transaction.atomic
    def create(self, validated_data):
        # return super().create(validated_data)
        user = self.context['request'].user
        items_data = validated_data.pop('items')

        total_amount = 0
        for item_data in items_data:
            food_item = FoodItem.objects.get(id=item_data['food_item_id'])
            total_amount += food_item.price * item_data['quantity']
            # item_data['price'] = food_item.price
            # item_data['subtotal'] = food_item.price * item_data['quantity']
            # total_amount += item_data['subtotal']

        order = Order.objects.create(
            user=user,
            total_price=total_amount,
            **validated_data
        )

        for item_data in items_data:
            food_item = FoodItem.objects.get(id=item_data['food_item_id'])
            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=item_data['quantity'],
                price=food_item.price
            )

        success = order.assign_restaurant_and_courier(user.delivery_latitude, user.delivery_longitude)
        
        if not success:
            order.status = 'CANCELLED'
            order.save()
            raise serializers.ValidationError("No restaurant or courier available")
        
        return order