"""
Script to create test data for Attendance Management System
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

from accounts.models import User
from companies.models import Company
from employees.models import Employee
from decimal import Decimal
from datetime import date, timedelta

print("=" * 60)
print("Creating Test Data for Attendance Management System")
print("=" * 60)

# Get or create admin user
admin = User.objects.filter(role='ADMIN').first()
if not admin:
    admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    admin.role = 'ADMIN'
    admin.save()
    print("Created admin user")

# ============================================
# CREATE COMPANIES
# ============================================
print("\n[COMPANIES]")
companies_data = [
    {'name': 'Tata Steel Industries', 'address': 'Jamshedpur, Jharkhand', 'contact_number': '9876543210', 'email': 'contact@tatasteel.com'},
    {'name': 'Reliance Power Plant', 'address': 'Surat, Gujarat', 'contact_number': '9876543211', 'email': 'info@reliancepower.com'},
    {'name': 'Adani Infrastructure', 'address': 'Ahmedabad, Gujarat', 'contact_number': '9876543212', 'email': 'hr@adani.com'},
    {'name': 'JSW Steel Works', 'address': 'Bellary, Karnataka', 'contact_number': '9876543213', 'email': 'careers@jsw.com'},
]

created_companies = {}
for data in companies_data:
    company, created = Company.objects.get_or_create(
        name=data['name'],
        defaults={**data, 'created_by': admin}
    )
    created_companies[data['name']] = company
    status = '[+] Created' if created else '[=] Exists'
    print(f"  {status}: {company.name}")

# ============================================
# CREATE SUPERVISORS
# ============================================
print("\n[SUPERVISORS]")
supervisors_data = [
    {
        'username': 'rajesh.sharma@test.com',
        'email': 'rajesh.sharma@test.com',
        'first_name': 'Rajesh',
        'last_name': 'Sharma',
        'mobile': '9898123456',
        'password': 'supervisor123',
        'companies': ['Tata Steel Industries', 'JSW Steel Works']
    },
    {
        'username': 'priya.patel@test.com',
        'email': 'priya.patel@test.com',
        'first_name': 'Priya',
        'last_name': 'Patel',
        'mobile': '9898123457',
        'password': 'supervisor123',
        'companies': ['Reliance Power Plant']
    },
    {
        'username': 'amit.kumar@test.com',
        'email': 'amit.kumar@test.com',
        'first_name': 'Amit',
        'last_name': 'Kumar',
        'mobile': '9898123458',
        'password': 'supervisor123',
        'companies': ['Adani Infrastructure']
    },
]

created_supervisors = {}
for data in supervisors_data:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'mobile': data['mobile'],
            'role': 'SUPERVISOR',
            'is_active': True
        }
    )
    if created:
        user.set_password(data['password'])
        user.save()
    
    # Assign companies
    for company_name in data['companies']:
        if company_name in created_companies:
            user.assigned_companies.add(created_companies[company_name])
    
    created_supervisors[data['username']] = user
    status = '[+] Created' if created else '[=] Exists'
    companies_list = ', '.join(data['companies'])
    print(f"  {status}: {user.get_full_name()} ({user.email})")
    print(f"           Assigned: {companies_list}")

# ============================================
# CREATE EMPLOYEES
# ============================================
print("\n[EMPLOYEES]")
employees_data = [
    # Tata Steel Employees
    {'employee_code': 'TATA001', 'first_name': 'Ravi', 'last_name': 'Singh', 'company': 'Tata Steel Industries', 'designation': 'Welder', 'salary_per_day': 800, 'ot_per_hour': 150, 'contact': '9900112233', 'email': 'ravi.singh@tata.com'},
    {'employee_code': 'TATA002', 'first_name': 'Suresh', 'last_name': 'Yadav', 'company': 'Tata Steel Industries', 'designation': 'Fitter', 'salary_per_day': 750, 'ot_per_hour': 140, 'contact': '9900112234', 'email': 'suresh.yadav@tata.com'},
    {'employee_code': 'TATA003', 'first_name': 'Mohan', 'last_name': 'Verma', 'company': 'Tata Steel Industries', 'designation': 'Electrician', 'salary_per_day': 900, 'ot_per_hour': 170, 'contact': '9900112235', 'email': 'mohan.verma@tata.com'},
    
    # Reliance Power Employees
    {'employee_code': 'REL001', 'first_name': 'Kiran', 'last_name': 'Desai', 'company': 'Reliance Power Plant', 'designation': 'Operator', 'salary_per_day': 850, 'ot_per_hour': 160, 'contact': '9900112236', 'email': 'kiran.desai@reliance.com'},
    {'employee_code': 'REL002', 'first_name': 'Meena', 'last_name': 'Shah', 'company': 'Reliance Power Plant', 'designation': 'Technician', 'salary_per_day': 820, 'ot_per_hour': 155, 'contact': '9900112237', 'email': 'meena.shah@reliance.com'},
    {'employee_code': 'REL003', 'first_name': 'Vijay', 'last_name': 'Mehta', 'company': 'Reliance Power Plant', 'designation': 'Helper', 'salary_per_day': 600, 'ot_per_hour': 100, 'contact': '9900112238', 'email': 'vijay.mehta@reliance.com'},
    
    # Adani Employees
    {'employee_code': 'ADN001', 'first_name': 'Ramesh', 'last_name': 'Joshi', 'company': 'Adani Infrastructure', 'designation': 'Supervisor', 'salary_per_day': 1000, 'ot_per_hour': 200, 'contact': '9900112239', 'email': 'ramesh.joshi@adani.com'},
    {'employee_code': 'ADN002', 'first_name': 'Sunita', 'last_name': 'Nair', 'company': 'Adani Infrastructure', 'designation': 'Engineer', 'salary_per_day': 1200, 'ot_per_hour': 250, 'contact': '9900112240', 'email': 'sunita.nair@adani.com'},
    {'employee_code': 'ADN003', 'first_name': 'Deepak', 'last_name': 'Gupta', 'company': 'Adani Infrastructure', 'designation': 'Foreman', 'salary_per_day': 950, 'ot_per_hour': 180, 'contact': '9900112241', 'email': 'deepak.gupta@adani.com'},
    
    # JSW Employees
    {'employee_code': 'JSW001', 'first_name': 'Anand', 'last_name': 'Reddy', 'company': 'JSW Steel Works', 'designation': 'Crane Operator', 'salary_per_day': 880, 'ot_per_hour': 165, 'contact': '9900112242', 'email': 'anand.reddy@jsw.com'},
    {'employee_code': 'JSW002', 'first_name': 'Lakshmi', 'last_name': 'Iyer', 'company': 'JSW Steel Works', 'designation': 'Quality Inspector', 'salary_per_day': 920, 'ot_per_hour': 175, 'contact': '9900112243', 'email': 'lakshmi.iyer@jsw.com'},
    {'employee_code': 'JSW003', 'first_name': 'Ganesh', 'last_name': 'Patil', 'company': 'JSW Steel Works', 'designation': 'Machine Operator', 'salary_per_day': 780, 'ot_per_hour': 145, 'contact': '9900112244', 'email': 'ganesh.patil@jsw.com'},
]

for i, data in enumerate(employees_data):
    company = created_companies.get(data['company'])
    if company:
        # Random join date in last 2 years
        join_date = date.today() - timedelta(days=30 * (i + 3))
        employee, created = Employee.objects.get_or_create(
            employee_code=data['employee_code'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'company': company,
                'designation': data['designation'],
                'salary_per_day': Decimal(str(data['salary_per_day'])),
                'ot_per_hour': Decimal(str(data['ot_per_hour'])),
                'contact_number': data['contact'],
                'email': data['email'],
                'date_of_joining': join_date,
                'is_active': True
            }
        )
        status = '[+] Created' if created else '[=] Exists'
        print(f"  {status}: {employee.employee_code} - {employee.get_full_name()} ({company.name})")

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Total Companies: {Company.objects.count()}")
print(f"  Total Users: {User.objects.count()}")
print(f"    - Admins: {User.objects.filter(role='ADMIN').count()}")
print(f"    - Supervisors: {User.objects.filter(role='SUPERVISOR').count()}")
print(f"  Total Employees: {Employee.objects.count()}")

print("\n" + "=" * 60)
print("LOGIN CREDENTIALS")
print("=" * 60)
print("\n  Admin:")
print("    Username: admin")
print("    Password: admin123")
print("\n  Supervisors (Password for all: supervisor123):")
for sup in supervisors_data:
    print(f"    - {sup['first_name']} {sup['last_name']}: {sup['username']}")
    
print("\n" + "=" * 60)
print("Test data created successfully!")
print("=" * 60)
