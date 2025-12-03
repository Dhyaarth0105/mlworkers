#!/usr/bin/env python
"""
Database initialization script for Attendance Management System
Creates database, runs migrations, and creates default users
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from django.core.management import call_command
from accounts.models import User


def init_database():
    """Initialize database with migrations and default data"""
    
    print("=" * 60)
    print("Attendance Management System - Database Initialization")
    print("=" * 60)
    
    # Run migrations
    print("\n[1/3] Running database migrations...")
    call_command('makemigrations')
    call_command('migrate')
    print("✓ Migrations completed successfully")
    
    # Create superuser if not exists
    print("\n[2/3] Creating default users...")
    
    # Create admin user
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='ADMIN'
        )
        print("✓ Admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")
    
    # Create supervisor user
    if not User.objects.filter(username='supervisor').exists():
        User.objects.create_user(
            username='supervisor',
            email='supervisor@example.com',
            password='supervisor123',
            role='SUPERVISOR'
        )
        print("✓ Supervisor user created (username: supervisor, password: supervisor123)")
    else:
        print("✓ Supervisor user already exists")
    
    # Collect static files
    print("\n[3/3] Collecting static files...")
    call_command('collectstatic', '--noinput', '--clear')
    print("✓ Static files collected successfully")
    
    print("\n" + "=" * 60)
    print("Database initialization completed successfully!")
    print("=" * 60)
    print("\nDefault Login Credentials:")
    print("-" * 60)
    print("Admin User:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nSupervisor User:")
    print("  Username: supervisor")
    print("  Password: supervisor123")
    print("-" * 60)
    print("\nYou can now run the development server with:")
    print("  python manage.py runserver")
    print("=" * 60)


if __name__ == '__main__':
    init_database()
