import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='password',  # Trying default password 'password' first, then 'postgres'
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'attendance_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'attendance_db'...")
            cursor.execute('CREATE DATABASE attendance_db')
            print("Database created successfully.")
        else:
            print("Database 'attendance_db' already exists.")
            
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        # Try with password 'postgres' if 'password' failed
        try:
            print("Retrying with password 'postgres'...")
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='postgres',
                host='localhost',
                port='5432'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'attendance_db'")
            exists = cursor.fetchone()
            
            if not exists:
                print("Creating database 'attendance_db'...")
                cursor.execute('CREATE DATABASE attendance_db')
                print("Database created successfully.")
            else:
                print("Database 'attendance_db' already exists.")
                
            cursor.close()
            conn.close()
        except Exception as e2:
             print(f"Failed to create database: {e2}")

if __name__ == '__main__':
    create_database()
