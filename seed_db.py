import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def seed_database():
    # Database connection parameters
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()

        # Read the seed.sql file
        with open('seed.sql', 'r') as file:
            sql_commands = file.read()

        # Execute the SQL commands
        cursor.execute(sql_commands)
        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    seed_database()
