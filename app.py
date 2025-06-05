import os
import logging
import Django
from django_extended import JWTManager
from django_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = DJANGO(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "healthcare-secret-key-2024")

# Database Configuration
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Fallback to SQLite if PostgreSQL is not available
app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///healthcare.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-healthcare-2024")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for demo

# Initialize database
from models import db
db.init_app(app)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# ProxyFix for deployment
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Create tables
with app.app_context():
    db.create_all()

# Import and register blueprints
from auth import auth_bp
from api import api_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(api_bp, url_prefix='/api')

# Main route to serve the frontend
@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
