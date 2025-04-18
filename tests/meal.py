import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from bson import ObjectId

from app.main import app
from app.models.meal import Meal, MealListItem, MealIngredient, IngredientInMeal
from app.models.ingredient import Ingredient
from app.exceptions.meal import MealNotFoundError, MealCreationError, MealValidationError

# Mock data
mock_ingredient_id = str(ObjectId())
mock_meal_id = str(ObjectId())
mock_user_id = "test_user_123"

mock_ingredient = {
    "_id": mock_ingredient_id,
    "name": "Apple",
    "description": "Fresh red apple",
    "quantity": 100.0,
    "unit": 1.0,
    "reference_quantity": 100.0,
    "reference_unit": "g",
    "nutrients": {
        "calories": 52.0,
        "protein": 0.3,
        "carbohydrates": 14.0,
        "fat": 0.2,
        "fiber": 2.4
    }
}

mock_meal_data = {
    "_id": mock_meal_id,
    "user_id": mock_user_id,
    "name": "Breakfast",
    "description": "Morning breakfast",
    "ingredients": [
        {
            "ingredient_id": mock_ingredient_id,
            "quantity": 200.0
        }
    ],
    "timestamp": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

mock_meal_input = {
    "_id": mock_meal_id,
    "user_id": mock_user_id,
    "name": "Breakfast",
    "description": "Morning breakfast",
    "ingredients": [
        {
            "ingredient": mock_ingredient_id,
            "quantity": 200.0
        }
    ],
    "timestamp": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat()
}

mock_meal_with_new_ingredient_input = {
    "_id": mock_meal_id,
    "user_id": mock_user_id,
    "name": "Lunch",
    "description": "Healthy lunch",
    "ingredients": [
        {
            "ingredient": {
                "_id": mock_ingredient_id,
                "name": "Banana",
                "description": "Yellow banana",
                "quantity": 120.0,
                "unit": 1.0,
                "reference_quantity": 100.0,
                "reference_unit": "g",
                "nutrients": {
                    "calories": 89.0,
                    "protein": 1.1,
                    "carbohydrates": 22.8,
                    "fat": 0.3,
                    "fiber": 2.6
                }
            },
            "quantity": 150.0
        }
    ],
    "timestamp": datetime.utcnow().isoformat()
}

mock_detailed_meal = {
    "_id": mock_meal_id,
    "user_id": mock_user_id,
    "name": "Breakfast",
    "description": "Morning breakfast",
    "ingredients": [
        {
            "name": "Apple",
            "quantity": 200.0,
            "nutrients": {
                "calories": {"value": 52.0, "unit": "kcal"},
                "protein": {"value": 0.3, "unit": "g"},
                "carbohydrates": {"value": 14.0, "unit": "g"},
                "fat": {"value": 0.2, "unit": "g"},
                "fiber": {"value": 2.4, "unit": "g"}
            }
        }
    ],
    "timestamp": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

# Setup test client with mocked dependencies
@pytest.fixture
def client():
    # Mock the dependencies
    app.dependency_overrides = {}
    
    # Mock authentication
    async def mock_get_current_user():
        return mock_user_id
    
    # Mock database
    async def mock_get_db():
        return MagicMock()
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db
    
    return TestClient(app)

# Tests for POST /meals/
@patch("app.api.v1.meal.create_meal_entry")
def test_create_meal_success(mock_create_meal, client):
    # Setup mock
    mock_create_meal.return_value = MealListItem(**mock_meal_data)
    
    # Make request
    response = client.post("/api/v1/meals/", json=mock_meal_input)
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["name"] == "Breakfast"
    assert response.json()["_id"] == mock_meal_id
    mock_create_meal.assert_called_once()

@patch("app.api.v1.meal.create_meal_entry")
def test_create_meal_with_new_ingredient(mock_create_meal, client):
    # Setup mock
    mock_create_meal.return_value = MealListItem(**mock_meal_data)
    
    # Make request
    response = client.post("/api/v1/meals/", json=mock_meal_with_new_ingredient_input)
    
    # Assertions
    assert response.status_code == 200
    mock_create_meal.assert_called_once()

@patch("app.api.v1.meal.create_meal_entry")
def test_create_meal_validation_error(mock_create_meal, client):
    # Setup mock
    mock_create_meal.side_effect = MealValidationError("Invalid meal data")
    
    # Make request
    response = client.post("/api/v1/meals/", json=mock_meal_input)
    
    # Assertions
    assert response.status_code == 422
    assert "Invalid meal data" in response.json()["detail"]

@patch("app.api.v1.meal.create_meal_entry")
def test_create_meal_database_error(mock_create_meal, client):
    # Setup mock
    mock_create_meal.side_effect = MealCreationError("Database error")
    
    # Make request
    response = client.post("/api/v1/meals/", json=mock_meal_input)
    
    # Assertions
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Tests for GET /meals/last
@patch("app.api.v1.meal.get_last_meal_entry_by_user")
def test_get_last_meal_success(mock_get_last_meal, client):
    # Setup mock
    mock_get_last_meal.return_value = MealListItem(**mock_meal_data)
    
    # Make request
    response = client.get("/api/v1/meals/last")
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["name"] == "Breakfast"
    assert response.json()["_id"] == mock_meal_id
    mock_get_last_meal.assert_called_once()

@patch("app.api.v1.meal.get_last_meal_entry_by_user")
def test_get_last_meal_not_found(mock_get_last_meal, client):
    # Setup mock
    mock_get_last_meal.side_effect = MealNotFoundError("No meals found")
    
    # Make request
    response = client.get("/api/v1/meals/last")
    
    # Assertions
    assert response.status_code == 404
    assert "No meals found" in response.json()["detail"]

@patch("app.api.v1.meal.get_last_meal_entry_by_user")
def test_get_last_meal_database_error(mock_get_last_meal, client):
    # Setup mock
    mock_get_last_meal.side_effect = MealCreationError("Database error")
    
    # Make request
    response = client.get("/api/v1/meals/last")
    
    # Assertions
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Tests for GET /meals/
@patch("app.api.v1.meal.get_paginated_meals_by_user")
def test_get_meals_paginated_success(mock_get_meals, client):
    # Setup mock
    mock_get_meals.return_value = ([MealListItem(**mock_meal_data)], 1)
    
    # Make request
    response = client.get("/api/v1/meals/?page=1&page_size=10")
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["page"] == 1
    assert response.json()["page_size"] == 10
    assert len(response.json()["meals"]) == 1
    assert response.json()["meals"][0]["name"] == "Breakfast"
    mock_get_meals.assert_called_once_with(MagicMock(), mock_user_id, 1, 10)

@patch("app.api.v1.meal.get_paginated_meals_by_user")
def test_get_meals_database_error(mock_get_meals, client):
    # Setup mock
    mock_get_meals.side_effect = MealCreationError("Database error")
    
    # Make request
    response = client.get("/api/v1/meals/")
    
    # Assertions
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Tests for GET /meals/{meal_id}/detailed
@patch("app.api.v1.meal.get_detailed_meal")
def test_get_detailed_meal_success(mock_get_detailed, client):
    # Setup mock
    mock_get_detailed.return_value = mock_detailed_meal
    
    # Make request
    response = client.get(f"/api/v1/meals/{mock_meal_id}/detailed")
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["name"] == "Breakfast"
    assert response.json()["_id"] == mock_meal_id
    assert len(response.json()["ingredients"]) == 1
    assert response.json()["ingredients"][0]["name"] == "Apple"
    assert "nutrients" in response.json()["ingredients"][0]
    mock_get_detailed.assert_called_once()

@patch("app.api.v1.meal.get_detailed_meal")
def test_get_detailed_meal_not_found(mock_get_detailed, client):
    # Setup mock
    mock_get_detailed.side_effect = MealNotFoundError("Meal not found")
    
    # Make request
    response = client.get(f"/api/v1/meals/{mock_meal_id}/detailed")
    
    # Assertions
    assert response.status_code == 404
    assert "Meal not found" in response.json()["detail"]

@patch("app.api.v1.meal.get_detailed_meal")
def test_get_detailed_meal_database_error(mock_get_detailed, client):
    # Setup mock
    mock_get_detailed.side_effect = MealCreationError("Database error")
    
    # Make request
    response = client.get(f"/api/v1/meals/{mock_meal_id}/detailed")
    
    # Assertions
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Service layer tests
@pytest.mark.asyncio
async def test_create_meal_entry_service():
    # Mock database
    mock_db = MagicMock()
    mock_db.ingredients.find_one = AsyncMock(return_value=mock_ingredient)
    mock_db.ingredients.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId(mock_ingredient_id)))
    
    # Mock repository function
    with patch("app.services.meal.create_meal", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_meal_id
        
        # Create meal object
        meal = Meal(**mock_meal_input)
        
        # Call service
        from app.services.meal import create_meal_entry
        result = await create_meal_entry(mock_db, meal, mock_user_id)
        
        # Assertions
        assert result.id == mock_meal_id
        assert result.name == "Breakfast"
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_get_last_meal_entry_service():
    # Mock database
    mock_db = MagicMock()
    
    # Mock repository function
    with patch("app.services.meal.get_last_meal_by_user", new_callable=AsyncMock) as mock_get_last:
        mock_get_last.return_value = mock_meal_data
        
        # Call service
        from app.services.meal import get_last_meal_entry_by_user
        result = await get_last_meal_entry_by_user(mock_db, mock_user_id)
        
        # Assertions
        assert result.id == mock_meal_id
        assert result.name == "Breakfast"
        mock_get_last.assert_called_once_with(mock_db, mock_user_id)

@pytest.mark.asyncio
async def test_get_paginated_meals_service():
    # Mock database
    mock_db = MagicMock()
    
    # Mock repository function
    with patch("app.services.meal.get_meals_by_user_paginated", new_callable=AsyncMock) as mock_get_paginated:
        mock_get_paginated.return_value = ([mock_meal_data], 1)
        
        # Call service
        from app.services.meal import get_paginated_meals_by_user
        meals, total = await get_paginated_meals_by_user(mock_db, mock_user_id, 1, 10)
        
        # Assertions
        assert len(meals) == 1
        assert meals[0].id == mock_meal_id
        assert total == 1
        mock_get_paginated.assert_called_once_with(mock_db, mock_user_id, 1, 10)

@pytest.mark.asyncio
async def test_get_detailed_meal_service():
    # Mock database
    mock_db = MagicMock()
    mock_db.meals.find_one = AsyncMock(return_value=mock_meal_data)
    mock_db.ingredients.find_one = AsyncMock(return_value=mock_ingredient)
    
    # Call service
    from app.services.meal import get_detailed_meal
    result = await get_detailed_meal(mock_db, mock_meal_id, mock_user_id)
    
    # Assertions
    assert result["_id"] == mock_meal_id
    assert result["name"] == "Breakfast"
    assert len(result["ingredients"]) == 1
    assert "nutrients" in result["ingredients"][0]
    
    mock_db.meals.find_one.assert_called_once_with({"_id": mock_meal_id, "user_id": mock_user_id})