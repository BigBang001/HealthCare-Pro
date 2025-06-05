from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from models import User
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('name', 'email', 'password')):
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Name, email, and password are required'
            }), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Basic validation
        if len(name) < 2:
            return jsonify({
                'error': 'Invalid name',
                'message': 'Name must be at least 2 characters long'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'error': 'Invalid password',
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400
        
        # Create user
        user = User.create(name, email, password)
        if not user:
            return jsonify({
                'error': 'Email already exists',
                'message': 'A user with this email already exists'
            }), 409
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        logging.info(f"New user registered: {email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Registration failed',
            'message': 'An error occurred during registration'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('email', 'password')):
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Email and password are required'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        logging.info(f"User logged in: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Login failed',
            'message': 'An error occurred during login'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'Current user not found'
            }), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Get current user error: {str(e)}")
        return jsonify({
            'error': 'Failed to get user',
            'message': 'An error occurred while fetching user data'
        }), 500
