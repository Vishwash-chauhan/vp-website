from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Sample featured experts data
    featured_experts = [
        {
            'name': 'John Smith',
            'title': 'Former VP at Google',
            'description': 'Startup strategy, product management, scaling teams',
            'avatar_url': 'images/experts/1.png',
            'reviews_count': 127,
            'hourly_rate': 200,
            'rating': 4.9
        },
        {
            'name': 'Sarah Davis',
            'title': 'Marketing Director at Tesla',
            'description': 'Growth marketing, brand strategy, digital campaigns',
            'avatar_url': 'images/experts/2.png',
            'reviews_count': 89,
            'hourly_rate': 150,
            'rating': 4.8
        },
        {
            'name': 'Michael Johnson',
            'title': 'Serial Entrepreneur',
            'description': 'Fundraising, scaling startups, business development',
            'avatar_url': 'images/experts/3.png',
            'reviews_count': 203,
            'hourly_rate': 300,
            'rating': 5.0
        }
    ]
    return render_template('index.html', active_page='home', experts=featured_experts)

@main.route('/experts')
def experts():
    return render_template('experts.html', active_page='experts')

@main.route('/club')
def club():
    return render_template('club.html', active_page='club')

@main.route('/about')
def about():
    return render_template('about.html', active_page='about')