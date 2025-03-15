from .models import FoodItem 
from rest_framework import permissions, viewsets
from .serializers import MenuItemSerializer

class MenuItemViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'item_id'
    serializer_class = MenuItemSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = FoodItem.objects.all()
        
        # Filter by price range if provided
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        category = self.request.query_params.get('category', None)
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price is not None:
            queryset = queryset.filter(price__lte=float(max_price))
        if category is not None:
            queryset = queryset.filter(category__iexact=category)
            
        return queryset

