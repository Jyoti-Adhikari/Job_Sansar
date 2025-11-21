from flask import Blueprint, render_template, send_from_directory, session, redirect, url_for, current_app

# SIMPLE blueprint - no static_folder configuration
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def homepage():
    if 'username' in session and 'role' in session:
        if session['role'] == 'candidate':
            return redirect(url_for('candidate.precandidate'))
        elif session['role'] == 'jobgiver':
            return redirect(url_for('jobgiver.prejobgiver'))
        elif session['role'] == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    return render_template('homepage.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/uploads/cvs/<filename>')
def uploaded_cv(filename):
    return send_from_directory(current_app.config['CANDIDATE_UPLOADS'], filename)

@main_bp.route('/uploads/jobs/<filename>')
def uploaded_job(filename):
    return send_from_directory(current_app.config['JOBGIVER_UPLOADS'], filename)