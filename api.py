from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from models import User, Patient, Doctor, PatientDoctorMapping
import logging

api_bp = Blueprint('api', __name__)

# Patient endpoints
@api_bp.route('/patients', methods=['POST'])
@jwt_required()
def create_patient():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('name', 'age', 'gender')):
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Name, age, and gender are required'
            }), 400
        
        name = data['name'].strip()
        age = data['age']
        gender = data['gender'].strip()
        medical_history = data.get('medical_history', '')
        
        # Basic validation
        if len(name) < 2:
            return jsonify({
                'error': 'Invalid name',
                'message': 'Name must be at least 2 characters long'
            }), 400
        
        if not isinstance(age, int) or age < 0 or age > 150:
            return jsonify({
                'error': 'Invalid age',
                'message': 'Age must be a number between 0 and 150'
            }), 400
        
        if gender.lower() not in ['male', 'female', 'other']:
            return jsonify({
                'error': 'Invalid gender',
                'message': 'Gender must be male, female, or other'
            }), 400
        
        # Create patient
        patient = Patient.create(name, age, gender, medical_history, current_user_id)
        
        logging.info(f"Patient created: {name} by user {current_user_id}")
        
        return jsonify({
            'message': 'Patient created successfully',
            'patient': patient.to_dict()
        }), 201
        
    except Exception as e:
        logging.error(f"Create patient error: {str(e)}")
        return jsonify({
            'error': 'Failed to create patient',
            'message': 'An error occurred while creating the patient'
        }), 500

@api_bp.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    try:
        current_user_id = get_jwt_identity()
        patients = Patient.get_by_user(current_user_id)
        
        return jsonify({
            'patients': [patient.to_dict() for patient in patients]
        }), 200
        
    except Exception as e:
        logging.error(f"Get patients error: {str(e)}")
        return jsonify({
            'error': 'Failed to get patients',
            'message': 'An error occurred while fetching patients'
        }), 500

@api_bp.route('/patients/<patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    try:
        current_user_id = get_jwt_identity()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({
                'error': 'Patient not found',
                'message': 'Patient with the specified ID does not exist'
            }), 404
        
        # Check if user owns this patient
        if patient.created_by_user_id != current_user_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only access patients you created'
            }), 403
        
        return jsonify({
            'patient': patient.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Get patient error: {str(e)}")
        return jsonify({
            'error': 'Failed to get patient',
            'message': 'An error occurred while fetching the patient'
        }), 500

@api_bp.route('/patients/<patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    try:
        current_user_id = get_jwt_identity()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({
                'error': 'Patient not found',
                'message': 'Patient with the specified ID does not exist'
            }), 404
        
        # Check if user owns this patient
        if patient.created_by_user_id != current_user_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only update patients you created'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Request body cannot be empty'
            }), 400
        
        # Update fields
        update_fields = {}
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                return jsonify({
                    'error': 'Invalid name',
                    'message': 'Name must be at least 2 characters long'
                }), 400
            update_fields['name'] = name
        
        if 'age' in data:
            age = data['age']
            if not isinstance(age, int) or age < 0 or age > 150:
                return jsonify({
                    'error': 'Invalid age',
                    'message': 'Age must be a number between 0 and 150'
                }), 400
            update_fields['age'] = age
        
        if 'gender' in data:
            gender = data['gender'].strip()
            if gender.lower() not in ['male', 'female', 'other']:
                return jsonify({
                    'error': 'Invalid gender',
                    'message': 'Gender must be male, female, or other'
                }), 400
            update_fields['gender'] = gender
        
        if 'medical_history' in data:
            update_fields['medical_history'] = data['medical_history']
        
        # Update patient
        patient.update(**update_fields)
        
        logging.info(f"Patient updated: {patient_id} by user {current_user_id}")
        
        return jsonify({
            'message': 'Patient updated successfully',
            'patient': patient.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Update patient error: {str(e)}")
        return jsonify({
            'error': 'Failed to update patient',
            'message': 'An error occurred while updating the patient'
        }), 500

@api_bp.route('/patients/<patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    try:
        current_user_id = get_jwt_identity()
        patient = Patient.get_by_id(patient_id)
        
        if not patient:
            return jsonify({
                'error': 'Patient not found',
                'message': 'Patient with the specified ID does not exist'
            }), 404
        
        # Check if user owns this patient
        if patient.created_by_user_id != current_user_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only delete patients you created'
            }), 403
        
        # Delete patient
        Patient.delete(patient_id)
        
        logging.info(f"Patient deleted: {patient_id} by user {current_user_id}")
        
        return jsonify({
            'message': 'Patient deleted successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Delete patient error: {str(e)}")
        return jsonify({
            'error': 'Failed to delete patient',
            'message': 'An error occurred while deleting the patient'
        }), 500

# Doctor endpoints
@api_bp.route('/doctors', methods=['POST'])
@jwt_required()
def create_doctor():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('name', 'specialization', 'experience_years')):
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Name, specialization, and experience_years are required'
            }), 400
        
        name = data['name'].strip()
        specialization = data['specialization'].strip()
        experience_years = data['experience_years']
        contact_info = data.get('contact_info', '')
        
        # Basic validation
        if len(name) < 2:
            return jsonify({
                'error': 'Invalid name',
                'message': 'Name must be at least 2 characters long'
            }), 400
        
        if len(specialization) < 2:
            return jsonify({
                'error': 'Invalid specialization',
                'message': 'Specialization must be at least 2 characters long'
            }), 400
        
        if not isinstance(experience_years, int) or experience_years < 0 or experience_years > 60:
            return jsonify({
                'error': 'Invalid experience years',
                'message': 'Experience years must be a number between 0 and 60'
            }), 400
        
        # Create doctor
        doctor = Doctor.create(name, specialization, experience_years, contact_info)
        
        logging.info(f"Doctor created: {name}")
        
        return jsonify({
            'message': 'Doctor created successfully',
            'doctor': doctor.to_dict()
        }), 201
        
    except Exception as e:
        logging.error(f"Create doctor error: {str(e)}")
        return jsonify({
            'error': 'Failed to create doctor',
            'message': 'An error occurred while creating the doctor'
        }), 500

@api_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    try:
        doctors = Doctor.get_all()
        
        return jsonify({
            'doctors': [doctor.to_dict() for doctor in doctors]
        }), 200
        
    except Exception as e:
        logging.error(f"Get doctors error: {str(e)}")
        return jsonify({
            'error': 'Failed to get doctors',
            'message': 'An error occurred while fetching doctors'
        }), 500

@api_bp.route('/doctors/<doctor_id>', methods=['GET'])
@jwt_required()
def get_doctor(doctor_id):
    try:
        doctor = Doctor.get_by_id(doctor_id)
        
        if not doctor:
            return jsonify({
                'error': 'Doctor not found',
                'message': 'Doctor with the specified ID does not exist'
            }), 404
        
        return jsonify({
            'doctor': doctor.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Get doctor error: {str(e)}")
        return jsonify({
            'error': 'Failed to get doctor',
            'message': 'An error occurred while fetching the doctor'
        }), 500

@api_bp.route('/doctors/<doctor_id>', methods=['PUT'])
@jwt_required()
def update_doctor(doctor_id):
    try:
        doctor = Doctor.get_by_id(doctor_id)
        
        if not doctor:
            return jsonify({
                'error': 'Doctor not found',
                'message': 'Doctor with the specified ID does not exist'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Request body cannot be empty'
            }), 400
        
        # Update fields
        update_fields = {}
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 2:
                return jsonify({
                    'error': 'Invalid name',
                    'message': 'Name must be at least 2 characters long'
                }), 400
            update_fields['name'] = name
        
        if 'specialization' in data:
            specialization = data['specialization'].strip()
            if len(specialization) < 2:
                return jsonify({
                    'error': 'Invalid specialization',
                    'message': 'Specialization must be at least 2 characters long'
                }), 400
            update_fields['specialization'] = specialization
        
        if 'experience_years' in data:
            experience_years = data['experience_years']
            if not isinstance(experience_years, int) or experience_years < 0 or experience_years > 60:
                return jsonify({
                    'error': 'Invalid experience years',
                    'message': 'Experience years must be a number between 0 and 60'
                }), 400
            update_fields['experience_years'] = experience_years
        
        if 'contact_info' in data:
            update_fields['contact_info'] = data['contact_info']
        
        # Update doctor
        doctor.update(**update_fields)
        
        logging.info(f"Doctor updated: {doctor_id}")
        
        return jsonify({
            'message': 'Doctor updated successfully',
            'doctor': doctor.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Update doctor error: {str(e)}")
        return jsonify({
            'error': 'Failed to update doctor',
            'message': 'An error occurred while updating the doctor'
        }), 500

@api_bp.route('/doctors/<doctor_id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(doctor_id):
    try:
        doctor = Doctor.get_by_id(doctor_id)
        
        if not doctor:
            return jsonify({
                'error': 'Doctor not found',
                'message': 'Doctor with the specified ID does not exist'
            }), 404
        
        # Delete doctor
        Doctor.delete(doctor_id)
        
        logging.info(f"Doctor deleted: {doctor_id}")
        
        return jsonify({
            'message': 'Doctor deleted successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Delete doctor error: {str(e)}")
        return jsonify({
            'error': 'Failed to delete doctor',
            'message': 'An error occurred while deleting the doctor'
        }), 500

# Patient-Doctor mapping endpoints
@api_bp.route('/mappings', methods=['POST'])
@jwt_required()
def create_mapping():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('patient_id', 'doctor_id')):
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Patient ID and Doctor ID are required'
            }), 400
        
        patient_id = data['patient_id']
        doctor_id = data['doctor_id']
        
        # Validate patient exists and user owns it
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return jsonify({
                'error': 'Patient not found',
                'message': 'Patient with the specified ID does not exist'
            }), 404
        
        if patient.created_by_user_id != current_user_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only assign doctors to patients you created'
            }), 403
        
        # Validate doctor exists
        doctor = Doctor.get_by_id(doctor_id)
        if not doctor:
            return jsonify({
                'error': 'Doctor not found',
                'message': 'Doctor with the specified ID does not exist'
            }), 404
        
        # Create mapping
        mapping = PatientDoctorMapping.create(patient_id, doctor_id, current_user_id)
        if not mapping:
            return jsonify({
                'error': 'Mapping already exists',
                'message': 'This doctor is already assigned to this patient'
            }), 409
        
        logging.info(f"Patient-Doctor mapping created: Patient {patient_id} - Doctor {doctor_id}")
        
        return jsonify({
            'message': 'Doctor assigned to patient successfully',
            'mapping': mapping.to_dict()
        }), 201
        
    except Exception as e:
        logging.error(f"Create mapping error: {str(e)}")
        return jsonify({
            'error': 'Failed to create mapping',
            'message': 'An error occurred while assigning the doctor to patient'
        }), 500

@api_bp.route('/mappings', methods=['GET'])
@jwt_required()
def get_mappings():
    try:
        mappings = PatientDoctorMapping.get_all()
        
        return jsonify({
            'mappings': [mapping.to_dict() for mapping in mappings]
        }), 200
        
    except Exception as e:
        logging.error(f"Get mappings error: {str(e)}")
        return jsonify({
            'error': 'Failed to get mappings',
            'message': 'An error occurred while fetching mappings'
        }), 500

@api_bp.route('/mappings/<patient_id>', methods=['GET'])
@jwt_required()
def get_patient_mappings(patient_id):
    try:
        current_user_id = get_jwt_identity()
        
        # Validate patient exists and user owns it
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return jsonify({
                'error': 'Patient not found',
                'message': 'Patient with the specified ID does not exist'
            }), 404
        
        if patient.created_by_user_id != current_user_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only view mappings for patients you created'
            }), 403
        
        mappings = PatientDoctorMapping.get_by_patient(patient_id)
        
        return jsonify({
            'mappings': [mapping.to_dict() for mapping in mappings]
        }), 200
        
    except Exception as e:
        logging.error(f"Get patient mappings error: {str(e)}")
        return jsonify({
            'error': 'Failed to get patient mappings',
            'message': 'An error occurred while fetching patient mappings'
        }), 500

@api_bp.route('/mappings/<mapping_id>', methods=['DELETE'])
@jwt_required()
def delete_mapping(mapping_id):
    try:
        current_user_id = get_jwt_identity()
        mapping = PatientDoctorMapping.get_by_id(mapping_id)
        
        if not mapping:
            return jsonify({
                'error': 'Mapping not found',
                'message': 'Mapping with the specified ID does not exist'
            }), 404
        
        # Check if user created this mapping
        if mapping.assigned_by_user_id != current_user_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You can only delete mappings you created'
            }), 403
        
        # Delete mapping
        PatientDoctorMapping.delete(mapping_id)
        
        logging.info(f"Patient-Doctor mapping deleted: {mapping_id}")
        
        return jsonify({
            'message': 'Mapping deleted successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Delete mapping error: {str(e)}")
        return jsonify({
            'error': 'Failed to delete mapping',
            'message': 'An error occurred while deleting the mapping'
        }), 500
