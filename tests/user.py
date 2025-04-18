import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId
from app.main import app
from app.models.user import UserCreate, UserLogin, UserOut
from fastapi import HTTPException

client = TestClient(app)

# Mock data
mock_user_id = str(ObjectId())
mock_user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}

mock_user_in_db = {
    "_id": ObjectId(mock_user_id),
    "username": "testuser",
    "email": "test@example.com",
    "password": "$2b$12$abcdefghijklmnopqrstuvwxyz"  # Mocked hashed password
}

mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Test user registration
@pytest.mark.asyncio
@patch('app.api.v1.user.register_user')
async def test_register_user_success(mock_register_user):
    # Setup
    mock_register_user.return_value = UserOut(
        id=mock_user_id,
        username=mock_user_data["username"],
        email=mock_user_data["email"]
    )
    
    # Execute
    response = client.post("/api/v1/users/register", json=mock_user_data)
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "id": mock_user_id,
        "username": mock_user_data["username"],
        "email": mock_user_data["email"]
    }
    mock_register_user.assert_called_once()

@pytest.mark.asyncio
@patch('app.api.v1.user.register_user')
async def test_register_user_duplicate_username(mock_register_user):
    # Setup
    mock_register_user.side_effect = HTTPException(status_code=400, detail="Username already exists")
    
    # Execute
    response = client.post("/api/v1/users/register", json=mock_user_data)
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

@pytest.mark.asyncio
async def test_register_user_invalid_data():
    # Execute
    invalid_data = mock_user_data.copy()
    invalid_data["email"] = "invalid-email"
    response = client.post("/api/v1/users/register", json=invalid_data)
    
    # Assert
    assert response.status_code == 422  # Pydantic validation error

# Test user login
@pytest.mark.asyncio
@patch('app.api.v1.user.login_user')
async def test_login_user_success(mock_login_user):
    # Setup
    mock_login_user.return_value = mock_token
    
    # Execute
    response = client.post("/api/v1/users/login", json={
        "username": mock_user_data["username"],
        "password": mock_user_data["password"]
    })
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "access_token": mock_token,
        "token_type": "bearer"
    }
    mock_login_user.assert_called_once()

@pytest.mark.asyncio
@patch('app.api.v1.user.login_user')
async def test_login_user_invalid_credentials(mock_login_user):
    # Setup
    mock_login_user.side_effect = HTTPException(status_code=401, detail="Invalid credentials")
    
    # Execute
    response = client.post("/api/v1/users/login", json={
        "username": "wronguser",
        "password": "wrongpassword"
    })
    
    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

# Test service layer functions
@pytest.mark.asyncio
@patch('app.services.user.create_user')
@patch('app.services.user.hash_password')
async def test_register_user_service(mock_hash_password, mock_create_user):
    # Setup
    from app.services.user import register_user
    
    mock_hash_password.return_value = "$2b$12$abcdefghijklmnopqrstuvwxyz"
    mock_create_user.return_value = mock_user_id
    mock_db = AsyncMock()
    
    # Execute
    user_create = UserCreate(**mock_user_data)
    result = await register_user(mock_db, user_create)
    
    # Assert
    assert isinstance(result, UserOut)
    assert result.id == mock_user_id
    assert result.username == mock_user_data["username"]
    assert result.email == mock_user_data["email"]
    mock_hash_password.assert_called_once_with(mock_user_data["password"])
    mock_create_user.assert_called_once()

@pytest.mark.asyncio
@patch('app.services.user.get_user_by_username')
@patch('app.services.user.verify_password')
@patch('app.services.user.create_access_token')
async def test_login_user_service(mock_create_token, mock_verify_password, mock_get_user):
    # Setup
    from app.services.user import login_user
    
    mock_get_user.return_value = mock_user_in_db
    mock_verify_password.return_value = True
    mock_create_token.return_value = mock_token
    mock_db = AsyncMock()
    
    # Execute
    result = await login_user(mock_db, mock_user_data["username"], mock_user_data["password"])
    
    # Assert
    assert result == mock_token
    mock_get_user.assert_called_once_with(mock_db, mock_user_data["username"])
    mock_verify_password.assert_called_once_with(
        mock_user_data["password"], 
        mock_user_in_db["password"]
    )
    mock_create_token.assert_called_once_with({"sub": str(mock_user_in_db["_id"])})

@pytest.mark.asyncio
@patch('app.services.user.get_user_by_username')
async def test_login_user_service_user_not_found(mock_get_user):
    # Setup
    from app.services.user import login_user
    
    mock_get_user.return_value = None
    mock_db = AsyncMock()
    
    # Execute and Assert
    with pytest.raises(HTTPException) as exc_info:
        await login_user(mock_db, "nonexistent", "password")
    
    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail

@pytest.mark.asyncio
@patch('app.services.user.get_user_by_username')
@patch('app.services.user.verify_password')
async def test_login_user_service_invalid_password(mock_verify_password, mock_get_user):
    # Setup
    from app.services.user import login_user
    
    mock_get_user.return_value = mock_user_in_db
    mock_verify_password.return_value = False
    mock_db = AsyncMock()
    
    # Execute and Assert
    with pytest.raises(HTTPException) as exc_info:
        await login_user(mock_db, mock_user_data["username"], "wrongpassword")
    
    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail

# Test repository layer functions
@pytest.mark.asyncio
async def test_create_user_repository():
    # Setup
    from app.repositories.user import create_user
    
    mock_db = AsyncMock()
    mock_db.users.insert_one.return_value = AsyncMock(inserted_id=ObjectId(mock_user_id))
    
    # Execute
    result = await create_user(mock_db, mock_user_data)
    
    # Assert
    assert result == mock_user_id
    mock_db.users.insert_one.assert_called_once_with(mock_user_data)

@pytest.mark.asyncio
async def test_get_user_by_username_repository():
    # Setup
    from app.repositories.user import get_user_by_username
    
    mock_db = AsyncMock()
    mock_db.users.find_one.return_value = mock_user_in_db
    
    # Execute
    result = await get_user_by_username(mock_db, mock_user_data["username"])
    
    # Assert
    assert result == mock_user_in_db
    mock_db.users.find_one.assert_called_once_with({"username": mock_user_data["username"]})

@pytest.mark.asyncio
async def test_get_user_by_username_not_found_repository():
    # Setup
    from app.repositories.user import get_user_by_username
    
    mock_db = AsyncMock()
    mock_db.users.find_one.return_value = None
    
    # Execute
    result = await get_user_by_username(mock_db, "nonexistent")
    
    # Assert
    assert result is None
    mock_db.users.find_one.assert_called_once_with({"username": "nonexistent"})