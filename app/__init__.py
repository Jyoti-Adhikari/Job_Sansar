from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
        static_folder='../static',      
        template_folder='../templates'  
    )
    
    # Configuration
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/job_portal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # FIX: Use absolute paths for upload folders
    base_dir = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(base_dir, '..', 'uploads')
    
    app.config['CANDIDATE_UPLOADS'] = os.path.join(UPLOAD_FOLDER, 'cvs')
    app.config['JOBGIVER_UPLOADS'] = os.path.join(UPLOAD_FOLDER, 'jobs')
    
    # Ensure upload directories exist
    os.makedirs(app.config['CANDIDATE_UPLOADS'], exist_ok=True)
    os.makedirs(app.config['JOBGIVER_UPLOADS'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints (your existing code...)
    from app.routes.auth import auth_bp
    from app.routes.candidate import candidate_bp
    from app.routes.jobgiver import jobgiver_bp
    from app.routes.matching import matching_bp
    from app.routes.messaging import messaging_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(jobgiver_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(main_bp)
    
    # Register existing blueprints
    from career_routes import career_bp
    from admin import admin_bp
    app.register_blueprint(career_bp)
    app.register_blueprint(admin_bp)
    
    # Import and register context processors
    from app.utils.helpers import utility_processor
    app.context_processor(utility_processor)
    
    return app