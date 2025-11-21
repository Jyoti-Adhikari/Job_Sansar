from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify, current_app
from app import db
from app.models import User, JobRequirement, CandidateCV, Shortlist
from werkzeug.utils import secure_filename
import os

jobgiver_bp = Blueprint('jobgiver', __name__)

@jobgiver_bp.route('/jobgiver', methods=['GET', 'POST'])
def jobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        if request.method == 'POST':
            file = request.files['job_file']
            domain = request.form.get('domain')
            if file and file.filename.lower().endswith('.pdf'):
                filename = secure_filename(file.filename)
                path = os.path.join(current_app.config['JOBGIVER_UPLOADS'], filename)
                file.save(path)
                new_job = JobRequirement(user_id=user.id, filename=filename, domain=domain)
                db.session.add(new_job)
                db.session.commit()
                flash("Job uploaded!", "success")
        job_files = JobRequirement.query.filter_by(user_id=user.id).all()
        return render_template('jobgiver.html', job_files=job_files, username=user.username)
    return redirect(url_for('auth.login'))

@jobgiver_bp.route('/prejobgiver')
def prejobgiver():
    if 'role' in session and session['role'] == 'jobgiver':
        cvs = CandidateCV.query.all()
        user = User.query.filter_by(username=session['username']).first()
        return render_template("prejobgiver.html", cvs=cvs, username=user.username)
    return redirect(url_for("auth.login"))

@jobgiver_bp.route('/jobgiver/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'role' in session and session['role'] == 'jobgiver':
        user = User.query.filter_by(username=session['username']).first()
        job = JobRequirement.query.filter_by(id=job_id, user_id=user.id).first()
        if job:
            path = os.path.join(current_app.config['JOBGIVER_UPLOADS'], job.filename)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(job)
            db.session.commit()
            flash("Job deleted successfully!", "success")
        else:
            flash("Job not found!", "error")
    return redirect(url_for('jobgiver.jobgiver'))

@jobgiver_bp.route('/shortlist-cv', methods=['POST'])
def shortlist_cv():
    if session.get('role') != 'jobgiver': 
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    cv_id = data.get('cv_id')
    
    try:
        cv_id = int(cv_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid CV ID"}), 400
    
    user = User.query.filter_by(username=session['username']).first()
    
    if Shortlist.query.filter_by(jobgiver_id=user.id, cv_id=cv_id).first():
        return jsonify({"error": "Already shortlisted"}), 400
        
    db.session.add(Shortlist(jobgiver_id=user.id, cv_id=cv_id))
    db.session.commit()
    return jsonify({"success": "Shortlisted!"})

@jobgiver_bp.route('/remove-shortlist', methods=['POST'])
def remove_shortlist():
    if session.get('role') != 'jobgiver': 
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    cv_id = data.get('cv_id')
    
    try:
        cv_id = int(cv_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid CV ID"}), 400
        
    user = User.query.filter_by(username=session['username']).first()
        
    item = Shortlist.query.filter_by(jobgiver_id=user.id, cv_id=cv_id).first()
    if not item: 
        return jsonify({"error": "Not found"}), 404
        
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": "Removed from shortlist"})

@jobgiver_bp.route('/shortlisted')
def shortlisted():
    if session.get('role') != 'jobgiver': 
        return redirect(url_for('auth.login'))
        
    user = User.query.filter_by(username=session['username']).first()
    shortlists = Shortlist.query.filter_by(jobgiver_id=user.id).all()
    
    items = []
    for shortlist in shortlists:
        cv = CandidateCV.query.get(shortlist.cv_id)
        if cv:
            cv_user = User.query.get(cv.user_id)
            items.append((shortlist, cv, cv_user))
    
    return render_template('shortlisted.html', items=items)