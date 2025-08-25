import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.database import get_db, Base
from app.auth import get_password_hash
from app.models import User

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    try:
        # Delete existing test user if any
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        # Create new test user
        hashed_password = get_password_hash("testpassword")
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password=hashed_password,
            disabled=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def test_login_success(test_user):
    """Test successful login"""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_username():
    """Test login with invalid username"""
    response = client.post(
        "/token",
        data={"username": "nonexistent", "password": "testpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_invalid_password(test_user):
    """Test login with invalid password"""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_current_user(test_user):
    """Test getting current user with valid token"""
    # First login to get token
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]
    
    # Use token to access protected endpoint
    response = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_get_current_user_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/users/me/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_get_current_user_no_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/users/me/")
    assert response.status_code == 401