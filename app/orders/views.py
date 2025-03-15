from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes =  [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['PENDING', 'PREPARING']:
            return Response({'detail': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    
        if not request.user.is_staff and order.user != request.user:
            return Response({'detail': 'You do not have permission to cancel this order'}, status=status.HTTP_403_FORBIDDEN)
        
        order.status = 'CANCELLED'
        order.save()

        if order.restaurant:
            order.restaurant.set_available()
        
        if order.courier:
            order.courier.set_available()

        return Response({'detail': 'Order cancelled'})

    @action(detail=False, methods=['get'])
    def history(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-order_time')
        page = self.paginate_queryset(orders)
        
        # Using select_related to efficiently fetch     restaurant data in a single query
        orders = orders.select_related('restaurant')
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get']) 
    def track(self, request, pk=None):
        order = self.get_object()

        if not request.user.is_staff and order.user != request.user:
            return Response({'detail': 'You do not have permission to track this order'}, status=status.HTTP_403_FORBIDDEN)
        
        data = {
            'order_id': order.id,
            'status': order.status,
            'estimated_delivery_time': order.estimated_delivery_time,
            'restaurant_name': order.restaurant.name if order.restaurant else None,
            'current_time': timezone.now()
        }

        return Response(data)
