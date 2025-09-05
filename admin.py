# admin.py
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app import db
from app import User, CandidateCV, JobRequirement  # import models from your app.py

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Admin Login ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check against database for username 'jyoti' only
        admin_user = User.query.filter_by(username='jyoti', password='jyoti').first()

        if admin_user and username == 'jyoti' and password == 'jyoti':
            session['admin'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Invalid admin credentials")

    return render_template('admin/login.html')

# --- Admin Dashboard ---
@admin_bp.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin.login'))

    users = User.query.all()
    jobs = JobRequirement.query.all()
    cvs = CandidateCV.query.all()

    return render_template(
        'admin/dashboard.html',
        users=users,
        jobs=jobs,
        cvs=cvs
    )

# --- Admin Logout ---
@admin_bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))
