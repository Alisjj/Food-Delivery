from django.urls import path

from .views import MenuItemViewSet

app_name = 'restaurants'

urlpatterns = [
    path('menu-items/', MenuItemViewSet.as_view({'get': 'list'}), name='menu_list'),
    path('menu-items/<uuid:item_id>/', MenuItemViewSet.as_view({'get': 'retrieve'}), name='menu_detail'),
]