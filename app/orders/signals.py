# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import Order, Restaurant
# from .tasks import update_restaurant_availability

# @receiver(post_save, sender=Order)
# def handle_order_status_change(sender, instance, created, **kwargs):
#     """
#     Handle automated actions when an order status changes
#     """
#     if created:
#         # If a new order is created, schedule restaurant availability update
#         update_restaurant_availability.apply_async(
#             eta=timezone.now() + timezone.timedelta(minutes=15)
#         )
#     else:
#         # If order status changes to DELIVERED, update restaurant availability
#         if instance.status == 'DELIVERED':
#             if instance.restaurant:
#                 instance.restaurant.set_available()
            
#             if instance.courier:
#                 instance.courier.complete_delivery()
