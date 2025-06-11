from flask import Blueprint, render_template, request, jsonify, abort
from app.models import Expert

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