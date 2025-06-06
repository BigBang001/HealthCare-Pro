 # 🏥HealthCare-Pro

A full-stack healthcare management system built with Django, PostreSQL, JWT authentication, and a modern Bootstrap frontend.

## Features

- User registration and login with JWT authentication
- Manage patients and doctors (CRUD)
- Assign doctors to patients
- Dashboard with statistics and charts

- Responsive UI with Bootstrap

## Screenshots

<div align="center">
  <img width = "100%" src="https://github.com/user-attachments/assets/adc7a5f6-9c6d-43ef-8b9b-09b97c979889">
 <p> Login Screen</p>
</div>

<br>
<div align="center">
  <img width = "100%" src="https://github.com/user-attachments/assets/d50b501b-314e-4d88-97cf-3ed9d15dea68">
 <p> Main Screen</p>
</div>
## Project Structure

```
├── healthcarepro/
 ├── __init__.py
 ├── apps.py
 ├── models.py
 ├── serializers.py
 ├── urls.py
 ├── views.py
 ├── wsgi.py
├── instance/
 ├── healthcare.db
├── static/
 ├──app.js
 ├── style.css          
├── templates/
 ├── index.html
├── manage.py
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


