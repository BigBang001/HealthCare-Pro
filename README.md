 # 🏥HealthCareConnect

A full-stack healthcare management system built with Flask, SQLAlchemy, JWT authentication, and a modern Bootstrap frontend.

## Features

- User registration and login with JWT authentication
- Manage patients and doctors (CRUD)
- Assign doctors to patients
- Dashboard with statistics and charts
- Responsive UI with Bootstrap

## Project Structure

```
healthcare_backend/
├── healthcare_backend/        # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/                      # Django app for APIs
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/BigBang001/HealthCareConnect.git
cd HealthCareConnect
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file (not committed to Git) for sensitive settings like secret keys and database URLs.

Example `.env`:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/healthcare.db
```

### 4. Run the Application

```sh
python main.py
```

The app will be available at [http://localhost:5000](http://localhost:5000).

## API Overview

- **Auth:**  
  - `POST /api/auth/register` – Register a new user  
  - `POST /api/auth/login` – Login and get JWT  
  - `GET /api/auth/me` – Get current user info

- **Patients:**  
  - `GET /api/patients` – List patients  
  - `POST /api/patients` – Add patient  
  - `PUT /api/patients/<id>` – Update patient  
  - `DELETE /api/patients/<id>` – Delete patient

- **Doctors:**  
  - `GET /api/doctors` – List doctors  
  - `POST /api/doctors` – Add doctor  
  - `PUT /api/doctors/<id>` – Update doctor  
  - `DELETE /api/doctors/<id>` – Delete doctor

- **Mappings:**  
  - `GET /api/mappings` – List all mappings  
  - `POST /api/mappings` – Assign doctor to patient  
  - `DELETE /api/mappings/<id>` – Remove assignment

All endpoints (except register/login) require a JWT token in the `Authorization: Bearer <token>` header.


