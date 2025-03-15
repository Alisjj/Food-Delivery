from django.utils import timezone
from celery import shared_task

@shared_task
def update_order_status(order_id):
    """
    Update order status to DELIVERED after 15 minutes
    """
    from ..restaurants.models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        
        if order.status in ['PREPARING', 'DELIVERING']:
            order.status = 'DELIVERED'
            order.save()
                
        return f"Updated order {order_id} status to DELIVERED"
    except Order.DoesNotExist:
        return f"Order {order_id} not found"
    except Exception as e:
        return f"Error updating order {order_id}: {str(e)}"
    

