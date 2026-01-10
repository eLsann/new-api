"""
Test authentication functionality.
"""
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import AdminUser
from app.security import hash_password


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_absensi.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test admin user
    admin = AdminUser(
        username="testadmin",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db.add(admin)
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_admin_login_success(test_db):
    """Test successful admin login."""
    response = client.post(
        "/admin/login",
        json={"username": "testadmin", "password": "testpass123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_admin_login_wrong_password(test_db):
    """Test login with wrong password."""
    response = client.post(
        "/admin/login",
        json={"username": "testadmin", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_admin_login_nonexistent_user(test_db):
    """Test login with nonexistent user."""
    response = client.post(
        "/admin/login",
        json={"username": "nonexistent", "password": "somepass"}
    )
    
    assert response.status_code == 401


def test_admin_login_missing_credentials(test_db):
    """Test login with missing credentials."""
    response = client.post(
        "/admin/login",
        json={"username": "", "password": ""}
    )
    
    assert response.status_code == 400


def test_protected_endpoint_without_token(test_db):
    """Test accessing protected endpoint without token."""
    response = client.get("/admin/persons")
    
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(test_db):
    """Test accessing protected endpoint with invalid token."""
    response = client.get(
        "/admin/persons",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(test_db):
    """Test accessing protected endpoint with valid token."""
    # First login
    login_response = client.post(
        "/admin/login",
        json={"username": "testadmin", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Then access protected endpoint
    response = client.get(
        "/admin/persons",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
