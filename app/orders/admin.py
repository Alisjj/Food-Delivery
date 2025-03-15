from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at', 'status']
    list_filter = [ 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'food_item', 'price', 'quantity']
    list_filter = ['order', 'food_item']
    search_fields = ['order__user__username', 'product__name']