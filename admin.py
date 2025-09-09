from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app import db, User, Feedback, CandidateCV, JobRequirement

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    users = User.query.all()
    jobs = JobRequirement.query.all()
    cvs = CandidateCV.query.all()
    return render_template('admin/dashboard.html', users=users, jobs=jobs, cvs=cvs)

@admin_bp.route('/admin/feedback', methods=['GET'])
def view_feedback():
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    feedback_list = Feedback.query.join(User).with_entities(
        Feedback.id, Feedback.message, Feedback.submitted_at, User.username
    ).order_by(Feedback.submitted_at.desc()).all()
    return render_template('admin/feedback.html', feedback_list=feedback_list)

@admin_bp.route('/admin/feedback/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    if 'role' not in session or session['role'] != 'admin':
        flash("You must be an admin to access this page.", "error")
        return redirect(url_for('login'))
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted successfully!", "success")
    return redirect(url_for('admin.view_feedback'))

@admin_bp.route('/admin/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))
