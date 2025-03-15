import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from restaurants.models import Restaurant, Courier, FoodItem
from orders.models import Order, OrderItem

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates test data for stakeholder testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--restaurants', type=int, default=3, help='Number of restaurants to create')
        parser.add_argument('--fooditems', type=int, default=15, help='Number of food items to create')
        # parser.add_argument('--orders', type=int, default=10, help='Number of orders to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before generating new data')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        self.create_users(options['users'])
        self.create_restaurants_and_couriers(options['restaurants'])
        self.create_food_items(options['fooditems'])
        # self.create_orders(options['orders'])

        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))

    def clear_data(self):
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        FoodItem.objects.all().delete()
        Courier.objects.all().delete()
        Restaurant.objects.all().delete()
        User.objects.filter(is_superuser=False, is_staff=False).delete()

    def create_users(self, count):
        self.stdout.write('Creating test users...')
        
        # Create a test admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'email_verified': True,
                'delivery_latitude': 40.7128,
                'delivery_longitude': -74.0060,
                'delivery_location': '123 Main St, New York, NY'
            }
        )
        
        if created:
            admin_user.set_password('adminpass')
            admin_user.save()
            self.stdout.write(f'Created admin user: admin/adminpass')

        # Create regular users
        for i in range(count):
            username = f'user{i+1}'
            email = f'user{i+1}@example.com'
            
            # Randomly assign locations around NYC
            lat_base, lng_base = 40.7128, -74.0060
            lat = lat_base + random.uniform(-0.05, 0.05)
            lng = lng_base + random.uniform(-0.05, 0.05)
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'email_verified': True,
                    'delivery_latitude': lat,
                    'delivery_longitude': lng,
                    'delivery_location': f'{i+1} Test Street, New York, NY'
                }
            )
            
            if created:
                user.set_password('password')
                user.save()
                self.stdout.write(f'Created user: {username}/password')

    def create_restaurants_and_couriers(self, count):
        self.stdout.write('Creating restaurants and couriers...')
        
        restaurant_names = [
            'Tasty Bites', 'Spice Palace', 'Green Garden', 'Burger Haven',
            'Pizza Paradise', 'Sushi Spot', 'Taco Town', 'Pasta Place'
        ]
        
        courier_names = [
            'John Smith', 'Maria Garcia', 'David Johnson', 'Lisa Brown',
            'Michael Wilson', 'Sarah Lee', 'Robert Taylor', 'Jennifer Davis'
        ]
        
        lat_base, lng_base = 40.7128, -74.0060
        
        for i in range(count):
            name = restaurant_names[i % len(restaurant_names)]
            if i > 0:
                name = f"{name} {i}"
                
            lat = lat_base + random.uniform(-0.03, 0.03)
            lng = lng_base + random.uniform(-0.03, 0.03)
            
            restaurant = Restaurant.objects.create(
                name=name,
                address=f'{100+i} Restaurant Avenue, New York, NY',
                latitude=lat,
                longitude=lng,
                is_active=True
            )
            
            courier_name = courier_names[i % len(courier_names)]
            if i > 0:
                courier_name = f"{courier_name} {i}"
                
            is_busy = random.random() < 0.2
            busy_until = timezone.now() + timedelta(minutes=15) if is_busy else None
            
            Courier.objects.create(
                restaurant=restaurant,
                name=courier_name,
                phone=f'555-{1000+i:04d}',
                busy_until=busy_until
            )
            
            self.stdout.write(f'Created restaurant: {name} with courier: {courier_name}')

    def create_food_items(self, count):
        self.stdout.write('Creating food items...')
        
        food_data = {
            'appetizer': [
                ('Mozzarella Sticks', 'Deep-fried mozzarella served with marinara sauce', Decimal('7.99')),
                ('Nachos', 'Corn chips topped with cheese, jalapeños, and salsa', Decimal('8.99')),
                ('Garlic Bread', 'Fresh bread with garlic butter', Decimal('4.99')),
                ('Spring Rolls', 'Crispy vegetable spring rolls', Decimal('6.99')),
            ],
            'main_course': [
                ('Cheeseburger', 'Classic burger with lettuce, tomato, and cheese', Decimal('12.99')),
                ('Margherita Pizza', 'Traditional pizza with tomato sauce and mozzarella', Decimal('14.99')),
                ('Grilled Chicken', 'Grilled chicken breast with vegetables', Decimal('15.99')),
                ('Beef Stir Fry', 'Stir-fried beef with vegetables', Decimal('16.99')),
                ('Vegetable Curry', 'Spicy vegetable curry with rice', Decimal('13.99')),
            ],
            'dessert': [
                ('Chocolate Cake', 'Rich chocolate cake with frosting', Decimal('6.99')),
                ('Ice Cream', 'Vanilla ice cream with chocolate sauce', Decimal('5.99')),
                ('Apple Pie', 'Homemade apple pie with cinnamon', Decimal('7.99')),
            ],
            'beverage': [
                ('Cola', 'Classic cola soda', Decimal('2.99')),
                ('Iced Tea', 'Fresh brewed iced tea', Decimal('2.49')),
                ('Lemonade', 'Fresh squeezed lemonade', Decimal('3.49')),
                ('Coffee', 'Locally roasted coffee', Decimal('2.99')),
            ],
            'side_dish': [
                ('French Fries', 'Crispy golden french fries', Decimal('3.99')),
                ('Onion Rings', 'Beer-battered onion rings', Decimal('4.99')),
                ('Side Salad', 'Fresh garden salad', Decimal('4.49')),
            ],
        }
        
        created_count = 0
        categories = list(food_data.keys())
        
        while created_count < count:
            category = random.choice(categories)
            items = food_data[category]
            item_data = items[created_count % len(items)]
            
            name, description, price = item_data
            
            # Add suffix to avoid duplicates
            if created_count >= len(items):
                name = f"{name} {created_count//len(items) + 1}"
            
            FoodItem.objects.create(
                name=name,
                description=description,
                price=price,
                image_url=f'https://example.com/food/{created_count+1}.jpg',
                category=category,
                is_available=random.random() > 0.1  # 90% of items available
            )
            
            created_count += 1
            if created_count % 5 == 0:
                self.stdout.write(f'Created {created_count} food items...')

    # def create_orders(self, count):
        self.stdout.write('Creating orders...')
        
        users = list(User.objects.filter(is_staff=False))
        if not users:
            users = list(User.objects.all())
        
        restaurants = list(Restaurant.objects.all())
        food_items = list(FoodItem.objects.filter(is_available=True))
        
        if not users or not restaurants or not food_items:
            self.stdout.write(self.style.WARNING('Not enough data to create orders'))
            return
        
        # Status distribution for test data
        status_weights = {
            'PENDING': 0.2,
            'PREPARING': 0.2, 
            'DELIVERING': 0.2,
            'DELIVERED': 0.3,
            'CANCELLED': 0.1
        }
        
        status_options = list(status_weights.keys())
        status_probabilities = list(status_weights.values())
        
        for i in range(count):
            user = random.choice(users)
            restaurant = random.choice(restaurants)
            courier = restaurant.courier
            
            # Create order with random status
            status = random.choices(status_options, status_probabilities)[0]
            
            # Create timestamps based on status
            now = timezone.now()
            if status == 'PENDING':
                order_time = now - timedelta(minutes=random.randint(1, 5))
                est_delivery = order_time + timedelta(minutes=15)
            elif status == 'PREPARING':
                order_time = now - timedelta(minutes=random.randint(5, 10))
                est_delivery = order_time + timedelta(minutes=15)
            elif status == 'DELIVERING':
                order_time = now - timedelta(minutes=random.randint(10, 15))
                est_delivery = order_time + timedelta(minutes=15)
            elif status == 'DELIVERED':
                order_time = now - timedelta(hours=random.randint(1, 48))
                est_delivery = order_time + timedelta(minutes=15)
            else:  
                order_time = now - timedelta(hours=random.randint(1, 24))
                est_delivery = order_time + timedelta(minutes=15)
            
            order = Order.objects.create(
                id=uuid.uuid4(),
                user=user,
                restaurant=restaurant,
                courier=courier if status != 'PENDING' else None,
                status=status,
                order_time=order_time,
                total_price=Decimal('0.00'), 
                estimated_delivery_time=est_delivery
            )
            
            num_items = random.randint(1, 5)
            total_price = Decimal('0.00')
            
            for _ in range(num_items):
                food_item = random.choice(food_items)
                quantity = random.randint(1, 3)
                price = food_item.price
                subtotal = price * quantity
                
                OrderItem.objects.create(
                    id=uuid.uuid4(),
                    order=order,
                    food_item=food_item,
                    quantity=quantity,
                    price=price
                )
                
                total_price += subtotal
            
            order.total_price = total_price
            order.save()
            
            if status in ['PREPARING', 'DELIVERING']:
                restaurant.busy_until = now + timedelta(minutes=15)
                restaurant.save()
                
                if courier:
                    courier.busy_until = now + timedelta(minutes=15)
                    courier.save()
            
            self.stdout.write(f'Created order #{i+1} with status {status} and {num_items} items')