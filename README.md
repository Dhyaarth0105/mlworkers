# Attendance Management System

A Django-based attendance management system with role-based access control for managing companies, employees, and daily attendance tracking.

## Features

- **Role-Based Access Control**
  - Admin: Full access to manage companies, employees, and view reports
  - Supervisor: Mark attendance and view attendance records

- **Company Management**
  - Add, edit, delete companies
  - Track company information and employees

- **Employee Management**
  - Add, edit, delete employees
  - Link employees to companies
  - Track employee details and attendance history

- **Attendance Tracking**
  - Mark individual attendance (Present/Absent/Overtime)
  - Bulk attendance marking
  - OT hours tracking
  - Attendance reports with filters
  - Export reports to CSV

## Technology Stack

- **Backend**: Django 4.2.7
- **Frontend**: Django Templates + Bootstrap 5
- **Database**: PostgreSQL
- **Additional Libraries**: Crispy Forms, ReportLab

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation

### 1. Create PostgreSQL Database

```sql
CREATE DATABASE attendance_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO postgres;
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the `.env` file with your database credentials:

```env
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5. Initialize Database

```bash
python init_db.py
```

This will:
- Run database migrations
- Create default admin and supervisor users
- Collect static files

### 6. Run Development Server

```bash
python manage.py runserver
```

Access the application at: `http://localhost:8000`

## Default Login Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Supervisor User:**
- Username: `supervisor`
- Password: `supervisor123`

**Important:** Change these passwords after first login!

## Project Structure

```
attendance_management_system/
├── attendance_project/     # Main project settings
├── accounts/              # User authentication & roles
├── companies/             # Company management
├── employees/             # Employee management
├── attendance/            # Attendance tracking
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── manage.py             # Django management script
├── init_db.py           # Database initialization
└── requirements.txt      # Python dependencies
```

## Usage

### Admin Features

1. **Dashboard**: View statistics and recent activity
2. **Companies**: Manage company information
3. **Employees**: Manage employee records
4. **Reports**: Generate and export attendance reports

### Supervisor Features

1. **Dashboard**: View today's attendance summary
2. **Mark Attendance**: Mark individual employee attendance
3. **Bulk Attendance**: Mark attendance for multiple employees
4. **View Records**: View attendance history

## Contributing

This is a custom project. For modifications or enhancements, please contact the development team.

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the system administrator.
