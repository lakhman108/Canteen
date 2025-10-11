import csv
import os
from django.core.management.base import BaseCommand
from canteen.models import Food, FoodDetails


class Command(BaseCommand):
    help = 'Seeds the database with data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing Food and FoodDetails data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            FoodDetails.objects.all().delete()
            Food.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

        # Get the base directory (where manage.py is located)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        food_csv_path = os.path.join(base_dir, 'canteen_food.csv')
        food_details_csv_path = os.path.join(base_dir, 'canteen_fooddetails.csv')

        # Check if files exist
        if not os.path.exists(food_csv_path):
            self.stdout.write(self.style.ERROR(f'Error: {food_csv_path} not found'))
            return
        
        if not os.path.exists(food_details_csv_path):
            self.stdout.write(self.style.ERROR(f'Error: {food_details_csv_path} not found'))
            return

        # Seed Food table
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Seeding Food Categories ==='))
        food_count = 0
        
        with open(food_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                food, created = Food.objects.update_or_create(
                    id=int(row['id']),
                    defaults={'name': row['name']}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created: {food.name} (ID: {food.id})'))
                else:
                    self.stdout.write(f'  Updated: {food.name} (ID: {food.id})')
                food_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✓ Total Food categories: {food_count}'))

        # Seed FoodDetails table
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Seeding Food Items ==='))
        food_details_count = 0
        errors = []

        with open(food_details_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Get the related Food object
                    food = Food.objects.get(id=int(row['food_id']))
                    
                    food_detail, created = FoodDetails.objects.update_or_create(
                        id=int(row['id']),
                        defaults={
                            'name': row['name'],
                            'stock_qty': int(row['stock_qty']),
                            'price': float(row['price']),
                            'photo_url': row['photo_url'],
                            'food': food,
                            'rating': int(row.get('rating', 0))
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'✓ Created: {food_detail.name} - ₹{food_detail.price} (ID: {food_detail.id})'))
                    else:
                        self.stdout.write(f'  Updated: {food_detail.name} - ₹{food_detail.price} (ID: {food_detail.id})')
                    
                    food_details_count += 1
                    
                except Food.DoesNotExist:
                    error_msg = f'Error: Food with id {row["food_id"]} does not exist for item "{row["name"]}"'
                    errors.append(error_msg)
                    self.stdout.write(self.style.ERROR(f'✗ {error_msg}'))
                except Exception as e:
                    error_msg = f'Error processing {row.get("name", "unknown")}: {str(e)}'
                    errors.append(error_msg)
                    self.stdout.write(self.style.ERROR(f'✗ {error_msg}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Total Food items: {food_details_count}'))

        # Summary
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'✓ Food categories seeded: {food_count}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Food items seeded: {food_details_count}'))
        
        if errors:
            self.stdout.write(self.style.ERROR(f'\n✗ Errors encountered: {len(errors)}'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        else:
            self.stdout.write(self.style.SUCCESS('\n🎉 Database seeded successfully with no errors!'))
