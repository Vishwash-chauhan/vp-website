from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Expert, User
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Get verified experts (as featured experts)
    featured_experts = Expert.get_verified()[:3]
    
    # If no verified experts, get first 3 available experts
    if not featured_experts:
        featured_experts = Expert.get_all_available()[:3]
    
    return render_template('index.html', active_page='home', experts=featured_experts)

@main.route('/experts')
def experts():
    # Get all available experts
    all_experts = Expert.get_all_available()
    return render_template('experts.html', active_page='experts', experts=all_experts)

@main.route('/expert/<int:expert_id>')
def expert_detail(expert_id):
    """Expert detail page"""
    expert = Expert.query.get_or_404(expert_id)
    
    # Get related experts (same expertise area, excluding current expert)
    related_experts = Expert.query.filter(
        Expert.expertise.contains(expert.expertise.split()[0]),  # First word of expertise
        Expert.id != expert_id,
        Expert.is_available == True
    ).limit(3).all()
    
    # If no related experts, get random available experts
    if not related_experts:
        related_experts = Expert.query.filter(
            Expert.id != expert_id,
            Expert.is_available == True
        ).limit(3).all()
    
    return render_template('expert_detail.html', active_page='experts', expert=expert, related_experts=related_experts)

@main.route('/api/experts/search')
def search_experts():
    """API endpoint for searching experts"""
    search_term = request.args.get('q', '')
    expertise = request.args.get('expertise', '')
    
    if search_term:
        experts = Expert.search_experts(search_term)
    elif expertise:
        experts = Expert.get_by_expertise(expertise)
    else:
        experts = Expert.get_all_available()
    
    return jsonify([expert.to_dict() for expert in experts])

@main.route('/club')
def club():
    return render_template('club.html', active_page='club')

@main.route('/about')
def about():
    return render_template('about.html', active_page='about')

@main.route('/dashboard')
@login_required
def dashboard():
    """Admin Dashboard with CRUD operations for Users and Experts"""
    # Get statistics
    total_users = User.query.count()
    total_experts = Expert.query.count()
    active_experts = Expert.query.filter_by(is_available=True).count()
    verified_experts = Expert.query.filter_by(is_verified=True).count()
    
    # Get recent users and experts for display
    recent_users = User.query.order_by(User.date_created.desc()).limit(5).all()
    recent_experts = Expert.query.order_by(Expert.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         active_page='dashboard',
                         total_users=total_users,
                         total_experts=total_experts,
                         active_experts=active_experts,
                         verified_experts=verified_experts,
                         recent_users=recent_users,
                         recent_experts=recent_experts)

@main.route('/dashboard/users')
@login_required
def dashboard_users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('dashboard_users.html', active_page='dashboard', users=users)

@main.route('/dashboard/experts')
@login_required  
def dashboard_experts():
    """Expert management page"""
    page = request.args.get('page', 1, type=int)
    experts = Expert.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('dashboard_experts.html', active_page='dashboard', experts=experts)

@main.route('/dashboard/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.name} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_users'))

@main.route('/dashboard/expert/<int:expert_id>/delete', methods=['POST'])
@login_required
def delete_expert(expert_id):
    """Delete an expert"""
    expert = Expert.query.get_or_404(expert_id)
    try:
        db.session.delete(expert)
        db.session.commit()
        flash(f'Expert {expert.name} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting expert: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_experts'))

@main.route('/dashboard/expert/<int:expert_id>/toggle-status', methods=['POST'])
@login_required
def toggle_expert_status(expert_id):
    """Toggle expert availability status"""
    expert = Expert.query.get_or_404(expert_id)
    try:
        expert.is_available = not expert.is_available
        db.session.commit()
        status = "available" if expert.is_available else "unavailable"
        flash(f'Expert {expert.name} is now {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating expert status: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_experts'))

@main.route('/dashboard/expert/<int:expert_id>/toggle-verification', methods=['POST'])
@login_required
def toggle_expert_verification(expert_id):
    """Toggle expert verification status"""
    expert = Expert.query.get_or_404(expert_id)
    try:
        expert.is_verified = not expert.is_verified
        db.session.commit()
        status = "verified" if expert.is_verified else "unverified"
        flash(f'Expert {expert.name} is now {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating expert verification: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_experts'))

@main.route('/dashboard/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def toggle_user_admin(user_id):
    """Toggle user admin status"""
    user = User.query.get_or_404(user_id)
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = "admin" if user.is_admin else "regular user"
        flash(f'User {user.name} is now a {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user admin status: {str(e)}', 'error')
    return redirect(url_for('main.dashboard_users'))