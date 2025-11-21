from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from app import db
from app.models import User, Feedback

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        user = User.query.filter_by(username=username, password=password, role=role).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            session['user_id'] = user.id 
            next_url = request.form.get('next') or ('/precandidate' if role == 'candidate' else '/prejobgiver' if role == 'jobgiver' else '/admin')
            return redirect(next_url)
        else:
            flash("Invalid login credentials.", "error")
    next_url = request.args.get('next', '')
    return render_template('login.html', next=next_url)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        address = request.form.get('address')
        company_name = request.form.get('company_name')

        if role == 'admin' and (username != 'jyoti' or password != 'jyoti'):
            flash("Admin role is restricted to username 'jyoti' and password 'jyoti'.", "error")
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return render_template('register.html')

        user = User(
            username=username,
            password=password,
            role=role,
            address=address,
            company_name=company_name
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'username' not in session:
        flash("You must log in to submit feedback.", "error")
        return redirect(url_for('auth.login', next=request.url))

    if request.method == 'POST':
        message = request.form.get('message')
        if not message or not message.strip():
            flash("Feedback message is required!", "error")
            return render_template('contact.html')
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash("User not found. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        feedback = Feedback(user_id=user.id, message=message)
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback submitted successfully!", "success")
        return redirect(url_for('auth.contact'))
    return render_template('contact.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('main.homepage'))