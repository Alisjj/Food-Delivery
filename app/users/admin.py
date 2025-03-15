from django.contrib import admin
from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    fields = (
        'id', 'username', 'first_name', 'last_name', 'delivery_location',
        'delivery_latitude', 'delivery_longitude', 'is_staff', 'is_active',
        'date_joined', 'last_login',
    )

    list_display = (
        'username', 'first_name', 'last_name', 'delivery_location',
        'is_staff', 'is_active', 'date_joined', 'last_login',
    )

    list_filter = ('is_staff', 'is_active', 'date_joined', 'last_login')
    readonly_fields = ('id', 'date_joined', 'last_login')
    search_fields = ('username', 'first_name', 'last_name', 'delivery_location') 
    