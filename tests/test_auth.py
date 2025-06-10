import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth(client):
    yield client

def test_login(auth):
    response = auth.post('/login', data={
        'contact': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b'Welcome Back' in response.data

def test_login_invalid(auth):
    response = auth.post('/login', data={
        'contact': 'invalid@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_signup(auth):
    response = auth.post('/signup', data={
        'contact': 'newuser@example.com',
        'password': 'newpassword123'
    })
    assert response.status_code == 201
    assert b'Successfully signed up' in response.data

def test_signup_existing_user(auth):
    auth.post('/signup', data={
        'contact': 'existinguser@example.com',
        'password': 'password123'
    })
    response = auth.post('/signup', data={
        'contact': 'existinguser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    assert b'User already exists' in response.data