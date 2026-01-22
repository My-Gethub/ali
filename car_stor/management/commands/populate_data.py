from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from car_stor.models import Category, Car, Accessory, BlogPost
from django.core.files import File
import os
import shutil
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with sample data from HTML template'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create users
        admin_user, root_user = self.create_users()
        
        # Create categories
        categories = self.create_categories()
        
        # Copy images
        self.copy_images()
        
        # Create cars
        cars_count = self.create_cars(admin_user, root_user, categories['Cars'])
        
        # Create accessories
        accessories_count = self.create_accessories(admin_user, root_user, categories)
        
        # Create blog posts
        blog_count = self.create_blog_posts(admin_user, root_user)
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Data population completed!'))
        self.stdout.write(self.style.SUCCESS(f'   - Users created: admin, root'))
        self.stdout.write(self.style.SUCCESS(f'   - Categories: {len(categories)}'))
        self.stdout.write(self.style.SUCCESS(f'   - Cars: {cars_count}'))
        self.stdout.write(self.style.SUCCESS(f'   - Accessories: {accessories_count}'))
        self.stdout.write(self.style.SUCCESS(f'   - Blog Posts: {blog_count}'))

    def create_users(self):
        """Create admin and root users"""
        self.stdout.write('Creating users...')
        
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@carstor.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('  [+] Admin user created'))
        else:
            self.stdout.write(self.style.WARNING('  [!] Admin user already exists'))
        
        # Create or get root user
        root_user, created = User.objects.get_or_create(
            username='root',
            defaults={
                'email': 'root@carstor.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            root_user.set_password('root123')
            root_user.save()
            self.stdout.write(self.style.SUCCESS('  [+] Root user created'))
        else:
            self.stdout.write(self.style.WARNING('  [!] Root user already exists'))
        
        return admin_user, root_user

    def create_categories(self):
        """Create product categories"""
        self.stdout.write('Creating categories...')
        
        category_names = [
            'Cars',
            'Audio',
            'Body Parts',
            'Exterior',
            'Interior',
            'Lighting',
            'Performance',
        ]
        
        categories = {}
        for name in category_names:
            category, created = Category.objects.get_or_create(name=name)
            categories[name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Category created: {name}'))
        
        return categories

    def copy_images(self):
        """Copy images from template to media directory"""
        self.stdout.write('Copying images...')
        
        template_images_path = r'd:\CAR_TRADE\STOR\harrier-car-dealer-html-responsive-template\harrier-car-dealer-html-responsive-template\products-images'
        media_path = r'd:\CAR_TRADE\STOR\media'
        
        # Create media directories if they don't exist
        os.makedirs(os.path.join(media_path, 'cars'), exist_ok=True)
        os.makedirs(os.path.join(media_path, 'accessories'), exist_ok=True)
        os.makedirs(os.path.join(media_path, 'blog'), exist_ok=True)
        
        # Copy car images (p1.jpg to p18.jpg)
        for i in range(1, 19):
            src = os.path.join(template_images_path, f'p{i}.jpg')
            dst = os.path.join(media_path, 'cars', f'p{i}.jpg')
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
        
        # Copy accessory images (p31.jpg to p49.jpg)
        for i in range(31, 50):
            src = os.path.join(template_images_path, f'p{i}.jpg')
            dst = os.path.join(media_path, 'accessories', f'p{i}.jpg')
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
        
        self.stdout.write(self.style.SUCCESS('  [+] Images copied'))

    def create_cars(self, admin_user, root_user, cars_category):
        """Create sample cars"""
        self.stdout.write('Creating cars...')
        
        car_data = [
            {
                'title': 'Mercedes-Benz E-Class All-Terrain Luxury',
                'price': Decimal('49000.00'),
                'old_price': Decimal('55000.00'),
                'description': 'Gorgeous Mercedes-Benz E-Class with all-terrain capability and luxury features. Perfect condition with full service history.',
                'model_year': 2018,
                'mileage': 4875,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '2.0L 4-Cylinder Turbo',
                'status': 'Used',
                'image': 'cars/p1.jpg',
            },
            {
                'title': 'BMW 5 Series Sedan Premium',
                'price': Decimal('45000.00'),
                'description': 'Luxury BMW 5 Series with premium features and excellent performance. Well maintained with low mileage.',
                'model_year': 2019,
                'mileage': 3200,
                'fuel_type': 'Diesel',
                'transmission': 'Automatic',
                'engine': '3.0L 6-Cylinder',
                'status': 'Used',
                'image': 'cars/p2.jpg',
            },
            {
                'title': 'Audi A6 Quattro Sport',
                'price': Decimal('52000.00'),
                'old_price': Decimal('58000.00'),
                'description': 'Sporty Audi A6 with Quattro all-wheel drive system. Loaded with technology and comfort features.',
                'model_year': 2020,
                'mileage': 2100,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '2.0L 4-Cylinder Turbo',
                'status': 'Used',
                'image': 'cars/p3.jpg',
            },
            {
                'title': 'Toyota Camry Hybrid LE',
                'price': Decimal('28000.00'),
                'description': 'Fuel-efficient Toyota Camry Hybrid with excellent reliability. Perfect for daily commuting.',
                'model_year': 2021,
                'mileage': 1500,
                'fuel_type': 'Hybrid',
                'transmission': 'Automatic',
                'engine': '2.5L 4-Cylinder Hybrid',
                'status': 'Used',
                'image': 'cars/p4.jpg',
            },
            {
                'title': 'Honda Accord Sport 2.0T',
                'price': Decimal('32000.00'),
                'description': 'Sporty Honda Accord with turbocharged engine. Great handling and modern technology.',
                'model_year': 2022,
                'mileage': 800,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '2.0L 4-Cylinder Turbo',
                'status': 'Used',
                'image': 'cars/p5.jpg',
            },
            {
                'title': 'Lexus ES 350 Luxury',
                'price': Decimal('42000.00'),
                'old_price': Decimal('47000.00'),
                'description': 'Premium Lexus ES 350 with exceptional comfort and reliability. Loaded with luxury features.',
                'model_year': 2020,
                'mileage': 2800,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '3.5L V6',
                'status': 'Used',
                'image': 'cars/p6.jpg',
            },
            {
                'title': 'Tesla Model 3 Long Range',
                'price': Decimal('48000.00'),
                'description': 'Electric Tesla Model 3 with long range battery. Autopilot enabled with latest software updates.',
                'model_year': 2023,
                'mileage': 500,
                'fuel_type': 'Electric',
                'transmission': 'Automatic',
                'engine': 'Dual Motor Electric',
                'status': 'Used',
                'image': 'cars/p7.jpg',
            },
            {
                'title': 'Ford Mustang GT Premium',
                'price': Decimal('55000.00'),
                'description': 'Powerful Ford Mustang GT with V8 engine. Performance package with premium interior.',
                'model_year': 2022,
                'mileage': 1200,
                'fuel_type': 'Petrol',
                'transmission': 'Manual',
                'engine': '5.0L V8',
                'status': 'Used',
                'image': 'cars/p8.jpg',
            },
            {
                'title': 'Chevrolet Corvette Stingray',
                'price': Decimal('75000.00'),
                'old_price': Decimal('82000.00'),
                'description': 'Stunning Chevrolet Corvette Stingray with mid-engine design. Ultimate sports car experience.',
                'model_year': 2023,
                'mileage': 300,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '6.2L V8',
                'status': 'New',
                'image': 'cars/p9.jpg',
            },
            {
                'title': 'Porsche 911 Carrera',
                'price': Decimal('95000.00'),
                'description': 'Iconic Porsche 911 Carrera with timeless design. Exceptional performance and handling.',
                'model_year': 2021,
                'mileage': 1800,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '3.0L 6-Cylinder Turbo',
                'status': 'Used',
                'image': 'cars/p10.jpg',
            },
            {
                'title': 'Nissan Altima SV',
                'price': Decimal('25000.00'),
                'description': 'Reliable Nissan Altima with modern features. Great value for money with low running costs.',
                'model_year': 2022,
                'mileage': 1100,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '2.5L 4-Cylinder',
                'status': 'Used',
                'image': 'cars/p11.jpg',
            },
            {
                'title': 'Mazda 6 Signature',
                'price': Decimal('30000.00'),
                'old_price': Decimal('34000.00'),
                'description': 'Elegant Mazda 6 with premium interior and smooth ride. Excellent build quality.',
                'model_year': 2021,
                'mileage': 1600,
                'fuel_type': 'Petrol',
                'transmission': 'Automatic',
                'engine': '2.5L 4-Cylinder Turbo',
                'status': 'Used',
                'image': 'cars/p12.jpg',
            },
        ]
        
        users = [admin_user, root_user]
        created_count = 0
        
        for i, data in enumerate(car_data):
            # Alternate between admin and root users
            seller = users[i % 2]
            
            # Random features
            data.update({
                'seller': seller,
                'category': cars_category,
                'air_conditioner': random.choice([True, False]),
                'power_windows': random.choice([True, False]),
                'power_steering': random.choice([True, True]),  # Most cars have this
                'central_locking': random.choice([True, False]),
                'abs': random.choice([True, True]),  # Most modern cars have ABS
                'airbags': random.choice([True, True]),  # Most modern cars have airbags
                'leather_seats': random.choice([True, False]),
            })
            
            car, created = Car.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            
            if created:
                created_count += 1
                owner = "admin" if seller == admin_user else "root"
                self.stdout.write(self.style.SUCCESS(f'  [+] Car created: {data["title"]} (Owner: {owner})'))
        
        return created_count

    def create_accessories(self, admin_user, root_user, categories):
        """Create sample accessories"""
        self.stdout.write('Creating accessories...')
        
        accessory_data = [
            # Audio accessories
            {
                'title': 'Premium Car Amplifier 1200W',
                'price': Decimal('299.99'),
                'old_price': Decimal('349.99'),
                'description': 'High-power car amplifier with crystal clear sound quality. Perfect for upgrading your car audio system.',
                'category': categories['Audio'],
                'image': 'accessories/p31.jpg',
            },
            {
                'title': 'Car Subwoofer 12-inch',
                'price': Decimal('199.99'),
                'description': 'Deep bass subwoofer for enhanced audio experience. Easy installation with mounting kit included.',
                'category': categories['Audio'],
                'image': 'accessories/p32.jpg',
            },
            {
                'title': 'Car Speaker Set 6.5-inch',
                'price': Decimal('149.99'),
                'old_price': Decimal('179.99'),
                'description': 'Premium quality car speakers with excellent sound reproduction. Set of 4 speakers.',
                'category': categories['Audio'],
                'image': 'accessories/p33.jpg',
            },
            # Body Parts
            {
                'title': 'Front Bumper Cover',
                'price': Decimal('399.99'),
                'description': 'OEM quality front bumper cover. Perfect fit and finish for various car models.',
                'category': categories['Body Parts'],
                'image': 'accessories/p34.jpg',
            },
            {
                'title': 'Chrome Front Grille',
                'price': Decimal('249.99'),
                'old_price': Decimal('299.99'),
                'description': 'Stylish chrome grille to enhance your car\'s appearance. Easy bolt-on installation.',
                'category': categories['Body Parts'],
                'image': 'accessories/p35.jpg',
            },
            # Exterior
            {
                'title': 'Car Cover All-Weather',
                'price': Decimal('89.99'),
                'description': 'Durable all-weather car cover. Protects against rain, snow, and UV rays.',
                'category': categories['Exterior'],
                'image': 'accessories/p36.jpg',
            },
            {
                'title': 'Body Kit Spoiler',
                'price': Decimal('449.99'),
                'old_price': Decimal('499.99'),
                'description': 'Aerodynamic spoiler for improved performance and sporty look.',
                'category': categories['Exterior'],
                'image': 'accessories/p37.jpg',
            },
            {
                'title': 'Side Mirror Covers Carbon Fiber',
                'price': Decimal('129.99'),
                'description': 'Premium carbon fiber mirror covers. Adds sporty touch to your vehicle.',
                'category': categories['Exterior'],
                'image': 'accessories/p38.jpg',
            },
            # Interior
            {
                'title': 'Leather Seat Covers Set',
                'price': Decimal('199.99'),
                'description': 'Premium leather seat covers for ultimate comfort. Universal fit for most vehicles.',
                'category': categories['Interior'],
                'image': 'accessories/p39.jpg',
            },
            {
                'title': 'Steering Wheel Cover',
                'price': Decimal('29.99'),
                'old_price': Decimal('39.99'),
                'description': 'Comfortable steering wheel cover with anti-slip grip. Available in multiple colors.',
                'category': categories['Interior'],
                'image': 'accessories/p40.jpg',
            },
            {
                'title': 'Dashboard Camera HD',
                'price': Decimal('149.99'),
                'description': 'Full HD dashboard camera with night vision. Loop recording and G-sensor included.',
                'category': categories['Interior'],
                'image': 'accessories/p41.jpg',
            },
            # Lighting
            {
                'title': 'LED Headlight Bulbs H7',
                'price': Decimal('79.99'),
                'old_price': Decimal('99.99'),
                'description': 'Super bright LED headlight bulbs. 6000K white light with long lifespan.',
                'category': categories['Lighting'],
                'image': 'accessories/p42.jpg',
            },
            {
                'title': 'Fog Light Kit',
                'price': Decimal('119.99'),
                'description': 'Complete fog light kit with wiring harness. Improves visibility in bad weather.',
                'category': categories['Lighting'],
                'image': 'accessories/p43.jpg',
            },
            {
                'title': 'LED Strip Lights Interior',
                'price': Decimal('39.99'),
                'description': 'RGB LED strip lights for car interior. Remote control with multiple color options.',
                'category': categories['Lighting'],
                'image': 'accessories/p44.jpg',
            },
            # Performance
            {
                'title': 'Cold Air Intake System',
                'price': Decimal('299.99'),
                'old_price': Decimal('349.99'),
                'description': 'Performance cold air intake for increased horsepower. Easy bolt-on installation.',
                'category': categories['Performance'],
                'image': 'accessories/p45.jpg',
            },
            {
                'title': 'Performance Exhaust System',
                'price': Decimal('599.99'),
                'description': 'Stainless steel exhaust system for improved performance and sound.',
                'category': categories['Performance'],
                'image': 'accessories/p46.jpg',
            },
            {
                'title': 'Brake Pad Set Performance',
                'price': Decimal('149.99'),
                'description': 'High-performance brake pads for better stopping power. Low dust formula.',
                'category': categories['Performance'],
                'image': 'accessories/p47.jpg',
            },
            {
                'title': 'Turbo Boost Controller',
                'price': Decimal('249.99'),
                'old_price': Decimal('299.99'),
                'description': 'Electronic boost controller for turbocharged engines. Adjustable boost levels.',
                'category': categories['Performance'],
                'image': 'accessories/p48.jpg',
            },
        ]
        
        users = [admin_user, root_user]
        created_count = 0
        
        for i, data in enumerate(accessory_data):
            # Alternate between admin and root users
            seller = users[i % 2]
            data['seller'] = seller
            
            accessory, created = Accessory.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            
            if created:
                created_count += 1
                owner = "admin" if seller == admin_user else "root"
                self.stdout.write(self.style.SUCCESS(f'  [+] Accessory created: {data["title"]} (Owner: {owner})'))
        
        return created_count

    def create_blog_posts(self, admin_user, root_user):
        """Create sample blog posts"""
        self.stdout.write('Creating blog posts...')
        
        blog_data = [
            {
                'title': 'Top 10 Car Maintenance Tips for 2024',
                'content': '''
                Keeping your car in top condition requires regular maintenance and attention. Here are our top 10 tips for 2024:
                
                1. Regular Oil Changes: Change your oil every 5,000-7,500 miles to keep your engine running smoothly.
                2. Check Tire Pressure: Maintain proper tire pressure for better fuel efficiency and safety.
                3. Replace Air Filters: Clean air filters improve engine performance and fuel economy.
                4. Inspect Brakes: Regular brake inspections can prevent costly repairs and ensure safety.
                5. Check Fluid Levels: Monitor coolant, brake fluid, and transmission fluid regularly.
                6. Battery Maintenance: Clean battery terminals and check voltage to avoid unexpected failures.
                7. Rotate Tires: Rotate tires every 6,000-8,000 miles for even wear.
                8. Replace Wiper Blades: Good visibility is crucial for safe driving.
                9. Check Lights: Ensure all lights are working properly for safety.
                10. Follow Service Schedule: Stick to your manufacturer's recommended service schedule.
                
                Regular maintenance not only extends your car's life but also maintains its resale value.
                ''',
                'image': 'blog/blog-img1.jpg',
            },
            {
                'title': 'Electric vs Hybrid: Which is Right for You?',
                'content': '''
                Choosing between an electric vehicle (EV) and a hybrid can be challenging. Let's break down the key differences:
                
                Electric Vehicles (EVs):
                - Zero emissions and environmentally friendly
                - Lower operating costs (no gas, less maintenance)
                - Instant torque and smooth acceleration
                - Requires charging infrastructure
                - Limited range compared to gas vehicles
                
                Hybrid Vehicles:
                - Combines gas engine with electric motor
                - Better fuel economy than traditional cars
                - No range anxiety - can use gas when needed
                - Lower emissions than gas-only vehicles
                - More expensive than conventional cars
                
                Consider your daily driving needs, access to charging, and budget when making your decision.
                The automotive industry is rapidly evolving, and both options offer significant benefits over traditional vehicles.
                ''',
                'image': 'blog/blog-img2.jpg',
            },
            {
                'title': 'Ultimate Guide to Car Audio Systems',
                'content': '''
                Upgrading your car's audio system can transform your driving experience. Here's what you need to know:
                
                Components of a Great Car Audio System:
                1. Head Unit: The brain of your system - choose one with modern features like Bluetooth and Apple CarPlay
                2. Speakers: Quality speakers make the biggest difference in sound quality
                3. Amplifier: Provides clean power to your speakers for better sound
                4. Subwoofer: Adds deep bass for a complete audio experience
                
                Installation Tips:
                - Start with speakers for the most noticeable improvement
                - Add an amplifier for more power and clarity
                - Consider sound deadening materials to reduce road noise
                - Professional installation ensures optimal performance
                
                Budget Considerations:
                - Entry level: $300-$500 (speakers and head unit)
                - Mid-range: $800-$1,500 (add amplifier and subwoofer)
                - High-end: $2,000+ (premium components and professional installation)
                
                A quality audio system enhances every drive and adds value to your vehicle.
                ''',
                'image': 'blog/blog-img3.jpg',
            },
            {
                'title': 'Best Performance Upgrades for Your Car',
                'content': '''
                Looking to boost your car's performance? Here are the most effective upgrades:
                
                Engine Upgrades:
                - Cold Air Intake: Increases airflow for more power
                - Performance Exhaust: Reduces backpressure and improves sound
                - ECU Tuning: Optimizes engine parameters for better performance
                - Turbocharger/Supercharger: Significant power gains
                
                Handling Upgrades:
                - Coilovers/Lowering Springs: Better handling and stance
                - Sway Bars: Reduces body roll in corners
                - Performance Tires: Improves grip and handling
                - Brake Upgrade: Essential for high-performance driving
                
                Start with bolt-on modifications and work your way up to more complex upgrades.
                Always consider the balance between power, handling, and reliability.
                ''',
                'image': 'blog/blog-img4.jpg',
            },
        ]
        
        users = [admin_user, root_user]
        created_count = 0
        
        for i, data in enumerate(blog_data):
            # Alternate between admin and root users
            author = users[i % 2]
            data['author'] = author
            
            blog_post, created = BlogPost.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            
            if created:
                created_count += 1
                owner = "admin" if author == admin_user else "root"
                self.stdout.write(self.style.SUCCESS(f'  [+] Blog post created: {data["title"]} (Author: {owner})'))
        
        return created_count
