from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import SignUpView, LogInView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/register/", SignUpView.as_view(), name='sign_up'),
    path("api/login/", LogInView.as_view(), name='log_in'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/restaurants/", include('restaurants.urls', 'restaurants')),
    path("api/orders/", include('orders.urls', 'orders')),
]
