import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

# Initialize database
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patients = db.relationship('Patient', backref='creator', lazy=True)
    mappings = db.relationship('PatientDoctorMapping', backref='assigner', lazy=True)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def create(cls, name, email, password):
        # Check if email already exists
        if cls.query.filter_by(email=email).first():
            return None
        
        user = cls(name, email, password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(user_id)

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    medical_history = db.Column(db.Text)
    created_by_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mappings = db.relationship('PatientDoctorMapping', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name, age, gender, medical_history, created_by_user_id):
        self.name = name
        self.age = age
        self.gender = gender
        self.medical_history = medical_history
        self.created_by_user_id = created_by_user_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'medical_history': self.medical_history,
            'created_by_user_id': self.created_by_user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_by_user_id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def create(cls, name, age, gender, medical_history, created_by_user_id):
        patient = cls(name, age, gender, medical_history, created_by_user_id)
        db.session.add(patient)
        db.session.commit()
        return patient
    
    @classmethod
    def get_by_id(cls, patient_id):
        return cls.query.get(patient_id)
    
    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter_by(created_by_user_id=user_id).all()
    
    @classmethod
    def delete(cls, patient_id):
        patient = cls.query.get(patient_id)
        if patient:
            db.session.delete(patient)
            db.session.commit()
            return True
        return False

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    contact_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mappings = db.relationship('PatientDoctorMapping', backref='doctor', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name, specialization, experience_years, contact_info):
        self.name = name
        self.specialization = specialization
        self.experience_years = experience_years
        self.contact_info = contact_info
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def create(cls, name, specialization, experience_years, contact_info):
        doctor = cls(name, specialization, experience_years, contact_info)
        db.session.add(doctor)
        db.session.commit()
        return doctor
    
    @classmethod
    def get_by_id(cls, doctor_id):
        return cls.query.get(doctor_id)
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def delete(cls, doctor_id):
        doctor = cls.query.get(doctor_id)
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            return True
        return False

class PatientDoctorMapping(db.Model):
    __tablename__ = 'patient_doctor_mappings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.String(36), db.ForeignKey('doctors.id'), nullable=False)
    assigned_by_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate mappings
    __table_args__ = (db.UniqueConstraint('patient_id', 'doctor_id', name='unique_patient_doctor'),)
    
    def __init__(self, patient_id, doctor_id, assigned_by_user_id):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.assigned_by_user_id = assigned_by_user_id
    
    def to_dict(self):
        patient = Patient.get_by_id(self.patient_id)
        doctor = Doctor.get_by_id(self.doctor_id)
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'patient_name': patient.name if patient else 'Unknown',
            'doctor_name': doctor.name if doctor else 'Unknown',
            'assigned_by_user_id': self.assigned_by_user_id,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def create(cls, patient_id, doctor_id, assigned_by_user_id):
        # Check if mapping already exists
        if cls.query.filter_by(patient_id=patient_id, doctor_id=doctor_id).first():
            return None
        
        mapping = cls(patient_id, doctor_id, assigned_by_user_id)
        db.session.add(mapping)
        db.session.commit()
        return mapping
    
    @classmethod
    def get_by_id(cls, mapping_id):
        return cls.query.get(mapping_id)
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_patient(cls, patient_id):
        return cls.query.filter_by(patient_id=patient_id).all()
    
    @classmethod
    def delete(cls, mapping_id):
        mapping = cls.query.get(mapping_id)
        if mapping:
            db.session.delete(mapping)
            db.session.commit()
            return True
        return False
