# User Management

A Django REST API for user authentication, registration, and profile management.

## Features
- JWT authentication
- User registration
- Profile auto-creation
- Update credentials
- Profile view and edit

## Setup
1. Clone the repository:
   ```sh
   git clone 
   cd User-Management
   ```
2. Create and activate a virtual environment:
   ```sh
   python3 -m venv myenv
   source myenv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```sh
   python manage.py migrate
   ```
5. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Running Tests
```sh
python manage.py test accounts
```

## API Endpoints
- `/api/register/` - Register a new user
- `/api/token/` - Obtain JWT token
- `/api/profiles/me/` - Get or update current user's profile
- `/api/profiles/` - List all profiles
- `/api/me/credentials/` - Update credentials

