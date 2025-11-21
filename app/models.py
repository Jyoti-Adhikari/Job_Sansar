from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    company_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CandidateCV(db.Model):
    __tablename__ = 'candidate_cvs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    domain = db.Column(db.String(100))
    user = db.relationship('User', backref='cvs')

class JobRequirement(db.Model):
    __tablename__ = 'job_requirements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    domain = db.Column(db.String(100))
    user = db.relationship('User', backref='job_requirements')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='feedback')

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_requirements.id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_id = db.Column(db.Integer, nullable=False)
    message_type = db.Column(db.String(20), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    related_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Shortlist(db.Model):
    __tablename__ = 'shortlists'
    id = db.Column(db.Integer, primary_key=True)
    jobgiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cv_id = db.Column(db.Integer, db.ForeignKey('candidate_cvs.id'), nullable=False)
    shortlisted_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_requirements.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

class CareerPath(db.Model):
    __tablename__ = 'career_paths'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.JSON)
    average_salary_min = db.Column(db.Integer)
    average_salary_max = db.Column(db.Integer)
    growth_outlook = db.Column(db.String(50))
    experience_level = db.Column(db.String(50))
    domain = db.Column(db.String(100))

class UserSkills(db.Model):
    __tablename__ = 'user_skills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    proficiency_level = db.Column(db.String(50))
    years_experience = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='skills')