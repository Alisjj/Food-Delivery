from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin


from .models import Restaurant, FoodItem, Courier


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    fields = (
        'id', 'name', 'address', 'latitude', 'longitude', 'is_active', 'busy_until',
        'created_at', 'updated_at',
    )

    list_display = ('name', 'address', 'is_active', 'busy_until', 'created_at', 'updated_at')
    list_filter = ('is_active', 'busy_until', 'created_at', 'updated_at')
    search_fields = ('name', 'address')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(FoodItem)
class MenuItemAdmin(admin.ModelAdmin):
    fields = (
        'id', 'name', 'description', 'price', 'image_url', 'category', 'is_available',
        'created_at', 'updated_at',
    )

    list_display = ('name', 'price', 'category', 'is_available', 'created_at', 'updated_at')
    list_filter = ('category', 'is_available', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    fields = (
        'id', 'name', 'phone', 'restaurant', 'busy_until', 'created_at', 'updated_at',
    )

    list_display = ('name', 'phone', 'busy_until', 'created_at', 'updated_at')
    list_filter = ('busy_until', 'created_at', 'updated_at')
    search_fields = ('name', 'phone')
    readonly_fields = ('id', 'created_at', 'updated_at')