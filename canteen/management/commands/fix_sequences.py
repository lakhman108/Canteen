from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

class Command(BaseCommand):
    help = 'Fix PostgreSQL sequences for auto-incrementing primary keys'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            type=str,
            help='Specific table name to fix (optional)',
        )

    def handle(self, *args, **options):
        tables_to_fix = []
        
        if options['table']:
            # Fix specific table
            tables_to_fix = [options['table']]
        else:
            # Get all tables from Django models
            for model in apps.get_models():
                table_name = model._meta.db_table
                tables_to_fix.append(table_name)
        
        with connection.cursor() as cursor:
            for table_name in tables_to_fix:
                try:
                    cursor.execute(f"""
                        SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), 
                               COALESCE((SELECT MAX(id) FROM {table_name}), 1) + 1, false);
                    """)
                    
                    # Get the new sequence value
                    cursor.execute(f"""
                        SELECT last_value FROM pg_sequences 
                        WHERE schemaname = 'public' AND sequencename = '{table_name}_id_seq'
                    """)
                    result = cursor.fetchone()
                    new_value = result[0] if result else 'N/A'
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Fixed {table_name}: next ID will be {new_value}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Skipped {table_name}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS('\nSuccessfully fixed all PostgreSQL sequences!')
        )