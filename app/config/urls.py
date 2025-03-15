from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import SignUpView, LogInView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include('users.urls', 'users')),
    path("api/restaurants/", include('restaurants.urls', 'restaurants')),
    path("api/orders/", include('orders.urls', 'orders')),
]
