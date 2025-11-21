from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session, jsonify
from app import db
from app.models import User, UserSkills, CareerPath
import os
import logging
import json

career_bp = Blueprint('career', __name__, url_prefix='/career')

class CareerPathPredictor:
    def __init__(self):
        self.career_paths = []
    
    def load_career_paths(self, career_paths_data):
        """Load career paths data"""
        self.career_paths = career_paths_data
    
    def predict_career_paths(self, user_skills, target_domain=None):
        """Predict suitable career paths based on skills"""
        recommendations = []
        
        for career in self.career_paths:
            if target_domain and target_domain != '-- All Domains --' and career['domain'] != target_domain:
                continue
            
            # Calculate match score
            match_score, matching_skills, missing_skills = self.calculate_match_score(user_skills, career)
            
            # Always show results, even with low match
            recommendations.append({
                'career_path': career,
                'match_score': match_score,
                'suitability': self.get_suitability_level(match_score),
                'missing_skills': missing_skills,
                'matching_skills': matching_skills
            })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations

    def calculate_match_score(self, user_skills, career):
        """Calculate how well user skills match career requirements"""
        # Parse required_skills from JSON string to list
        required_skills = []
        if career.get('required_skills'):
            if isinstance(career['required_skills'], str):
                try:
                    required_skills = json.loads(career['required_skills'])
                except:
                    # If JSON parsing fails, treat as comma-separated
                    required_skills = [s.strip() for s in career['required_skills'].split(',')]
            else:
                required_skills = career['required_skills']
        
        # Get user skill names (lowercase for comparison)
        user_skill_names = [skill['name'].lower() for skill in user_skills]
        
        matched_skills = 0
        matching_skills_list = []
        missing_skills_list = []
        
        for req_skill in required_skills:
            req_skill_lower = req_skill.lower()
            found = False
            
            # Check if any user skill matches the required skill
            for user_skill in user_skill_names:
                if req_skill_lower in user_skill or user_skill in req_skill_lower:
                    matched_skills += 1
                    matching_skills_list.append(req_skill)
                    found = True
                    break
            
            if not found:
                missing_skills_list.append(req_skill)
        
        # Calculate match percentage
        if required_skills:
            match_score = int((matched_skills / len(required_skills)) * 100)
        else:
            match_score = 50  # Default score if no requirements
        
        return match_score, matching_skills_list, missing_skills_list
    
    def get_suitability_level(self, match_score):
        """Get suitability level based on match score"""
        if match_score >= 80:
            return "Excellent Fit"
        elif match_score >= 60:
            return "Good Fit"
        elif match_score >= 40:
            return "Moderate Fit"
        else:
            return "Basic Fit"

@career_bp.route('/career-predictor')
def career_predictor():
    if 'username' not in session:
        flash('Please login to use career predictor', 'error')
        return redirect(url_for('auth.login'))  # Changed from 'login' to 'auth.login'
    
    user = User.query.filter_by(username=session['username']).first()
    user_skills = UserSkills.query.filter_by(user_id=user.id).all()
    
    # Get all available domains from career paths
    career_domains = db.session.query(CareerPath.domain).distinct().all()
    user_domains = [domain[0] for domain in career_domains]
    
    return render_template('career/predictor.html', 
                         user_skills=user_skills, 
                         user_domains=user_domains)

@career_bp.route('/career-predictor/analyze', methods=['POST'])
def analyze_career():
    if 'username' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    data = request.get_json()
    selected_domain = data.get('domain')
    
    # Get user's manually added skills
    manual_skills = UserSkills.query.filter_by(user_id=user.id).all()
    all_skills = []
    
    # Add manual skills
    for skill in manual_skills:
        all_skills.append({
            'name': skill.skill_name,
            'type': 'manual',
            'proficiency': skill.proficiency_level,
            'domain': 'General'
        })
    
    # Get career paths for the selected domain
    if selected_domain and selected_domain != '-- All Domains --':
        career_paths = CareerPath.query.filter_by(domain=selected_domain).all()
    else:
        career_paths = CareerPath.query.all()
    
    # Convert career paths to dictionary format
    career_paths_data = []
    for path in career_paths:
        career_paths_data.append({
            'id': path.id,
            'title': path.title,
            'description': path.description,
            'required_skills': path.required_skills,
            'average_salary_min': path.average_salary_min,
            'average_salary_max': path.average_salary_max,
            'growth_outlook': path.growth_outlook,
            'experience_level': path.experience_level,
            'domain': path.domain
        })
    
    # Get predictions
    predictor = CareerPathPredictor()
    predictor.load_career_paths(career_paths_data)
    
    # Calculate average experience from manual skills - FIXED
    total_experience = 0
    if manual_skills:
        total_experience = sum([skill.years_experience for skill in manual_skills]) / len(manual_skills)
    else:
        total_experience = 2  # Default
    
    recommendations = predictor.predict_career_paths(all_skills, selected_domain)
    
    return jsonify({
        'success': True,
        'recommendations': recommendations,
        'skills_found': len(all_skills),
        'user_experience': round(total_experience, 1),
        'selected_domain': selected_domain
    })

@career_bp.route('/career-predictor/skills', methods=['GET', 'POST'])
def manage_skills():
    if 'username' not in session:
        return redirect(url_for('auth.login'))  # Changed from 'login' to 'auth.login'
    
    user = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        skill_name = request.form.get('skill_name')
        proficiency = request.form.get('proficiency_level')
        years_exp = request.form.get('years_experience', 0)
        
        # Check if skill already exists
        existing_skill = UserSkills.query.filter_by(
            user_id=user.id, 
            skill_name=skill_name
        ).first()
        
        if existing_skill:
            existing_skill.proficiency_level = proficiency
            existing_skill.years_experience = years_exp
            flash('Skill updated successfully!', 'success')
        else:
            new_skill = UserSkills(
                user_id=user.id,
                skill_name=skill_name,
                proficiency_level=proficiency,
                years_experience=float(years_exp) if years_exp else 0
            )
            db.session.add(new_skill)
            flash('Skill added successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('career.manage_skills'))
    
    user_skills = UserSkills.query.filter_by(user_id=user.id).all()
    return render_template('career/skills.html', skills=user_skills)

@career_bp.route('/career-predictor/skills/delete/<int:skill_id>')
def delete_skill(skill_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))  # Changed from 'login' to 'auth.login'
    
    user = User.query.filter_by(username=session['username']).first()
    skill = UserSkills.query.get_or_404(skill_id)
    
    if skill.user_id != user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('career.manage_skills'))
    
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted successfully', 'success')
    return redirect(url_for('career.manage_skills'))

@career_bp.route('/career-predictor/domains')
def get_domains():
    if 'username' not in session:
        return jsonify({'error': 'Please login first'}), 401
        
    domains = db.session.query(CareerPath.domain).distinct().all()
    domain_list = [domain[0] for domain in domains]
    return jsonify({'domains': domain_list})

@career_bp.route('/career-predictor/skills/clear', methods=['POST'])
def clear_all_skills():
    if 'username' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    user = User.query.filter_by(username=session['username']).first()
    
    try:
        # Delete all user skills
        UserSkills.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'All skills cleared successfully'})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error clearing skills: {str(e)}")
        return jsonify({'error': 'Failed to clear skills'}), 500