import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from bson import ObjectId
from app.main import app
from app.models.ingredient import Ingredient
from app.exceptions.ingredient import IngredientCreationError, IngredientAlreadyExistsError, IngredientSearchError

client = TestClient(app)

# Mock data for testing
mock_ingredient_data = {
    "_id": "507f1f77bcf86cd799439011",
    "name": "Chicken Breast",
    "description": "Boneless, skinless chicken breast",
    "quantity": 100.0,
    "unit": 1.0,
    "reference_quantity": 100.0,
    "reference_unit": "g",
    "nutrients": {
        "protein": 31.0,
        "fat": 3.6,
        "carbohydrates": 0.0,
        "calories": 165.0
    }
}

mock_ingredient_list = [
    {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Chicken Breast",
        "description": "Boneless, skinless chicken breast",
        "quantity": 100.0,
        "unit": 1.0,
        "reference_quantity": 100.0,
        "reference_unit": "g",
        "nutrients": {
            "protein": 31.0,
            "fat": 3.6,
            "carbohydrates": 0.0,
            "calories": 165.0
        }
    },
    {
        "_id": "507f1f77bcf86cd799439012",
        "name": "Brown Rice",
        "description": "Whole grain brown rice",
        "quantity": 100.0,
        "unit": 1.0,
        "reference_quantity": 100.0,
        "reference_unit": "g",
        "nutrients": {
            "protein": 2.6,
            "fat": 0.9,
            "carbohydrates": 23.0,
            "calories": 112.0
        }
    }
]

mock_search_results = [
    {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Chicken Breast",
        "description": "Boneless, skinless chicken breast",
        "quantity": 100.0,
        "unit": 1.0,
        "reference_quantity": 100.0,
        "reference_unit": "g",
        "nutrients": {
            "protein": 31.0,
            "fat": 3.6,
            "carbohydrates": 0.0,
            "calories": 165.0
        }
    }
]

# Mock authentication
@pytest.fixture
def mock_auth():
    with patch("app.dependencies.auth.get_current_user", return_value="test_user_id"):
        yield

# Test creating a new ingredient - success case
@pytest.mark.asyncio
async def test_create_ingredient_success(mock_auth):
    with patch("app.services.ingredient.repo_create_ingredient", return_value=ObjectId(mock_ingredient_data["_id"])):
        response = client.post(
            "/api/v1/ingredients/",
            json={
                "name": "Chicken Breast",
                "description": "Boneless, skinless chicken breast",
                "quantity": 100.0,
                "unit": 1.0,
                "reference_quantity": 100.0,
                "reference_unit": "g",
                "nutrients": {
                    "protein": 31.0,
                    "fat": 3.6,
                    "carbohydrates": 0.0,
                    "calories": 165.0
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Chicken Breast"
        assert data["id"] == mock_ingredient_data["_id"]

# Test creating a new ingredient - already exists
@pytest.mark.asyncio
async def test_create_ingredient_already_exists(mock_auth):
    with patch("app.services.ingredient.repo_create_ingredient", 
               side_effect=IngredientAlreadyExistsError("Ingredient with name 'Chicken Breast' already exists")):
        response = client.post(
            "/api/v1/ingredients/",
            json={
                "name": "Chicken Breast",
                "description": "Boneless, skinless chicken breast",
                "quantity": 100.0,
                "unit": 1.0,
                "reference_quantity": 100.0,
                "reference_unit": "g",
                "nutrients": {
                    "protein": 31.0,
                    "fat": 3.6,
                    "carbohydrates": 0.0,
                    "calories": 165.0
                }
            }
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

# Test creating a new ingredient - database error
@pytest.mark.asyncio
async def test_create_ingredient_database_error(mock_auth):
    with patch("app.services.ingredient.repo_create_ingredient", 
               side_effect=IngredientCreationError("Failed to create ingredient due to a database error")):
        response = client.post(
            "/api/v1/ingredients/",
            json={
                "name": "Chicken Breast",
                "description": "Boneless, skinless chicken breast",
                "quantity": 100.0,
                "unit": 1.0,
                "reference_quantity": 100.0,
                "reference_unit": "g",
                "nutrients": {
                    "protein": 31.0,
                    "fat": 3.6,
                    "carbohydrates": 0.0,
                    "calories": 165.0
                }
            }
        )
        assert response.status_code == 500
        assert "database error" in response.json()["detail"]

# Test listing all ingredients - success case
@pytest.mark.asyncio
async def test_list_ingredients_success(mock_auth):
    with patch("app.services.ingredient.repo_get_ingredients", return_value=mock_ingredient_list):
        response = client.get("/api/v1/ingredients/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Chicken Breast"
        assert data[1]["name"] == "Brown Rice"

# Test listing all ingredients - database error
@pytest.mark.asyncio
async def test_list_ingredients_database_error(mock_auth):
    with patch("app.services.ingredient.repo_get_ingredients", 
               side_effect=IngredientCreationError("Failed to retrieve ingredients due to a database error")):
        response = client.get("/api/v1/ingredients/")
        assert response.status_code == 500
        assert "database error" in response.json()["detail"]

# Test searching ingredients - success case
@pytest.mark.asyncio
async def test_search_ingredients_success(mock_auth):
    with patch("app.services.ingredient.repo_search_ingredients", return_value=mock_search_results):
        response = client.get("/api/v1/ingredients/search?query=chicken")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Chicken Breast"

# Test searching ingredients - empty results
@pytest.mark.asyncio
async def test_search_ingredients_empty_results(mock_auth):
    with patch("app.services.ingredient.repo_search_ingredients", return_value=[]):
        response = client.get("/api/v1/ingredients/search?query=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

# Test searching ingredients - database error
@pytest.mark.asyncio
async def test_search_ingredients_database_error(mock_auth):
    with patch("app.services.ingredient.repo_search_ingredients", 
               side_effect=IngredientSearchError("Failed to search ingredients due to a database error")):
        response = client.get("/api/v1/ingredients/search?query=chicken")
        assert response.status_code == 500
        assert "database error" in response.json()["detail"]

# Test missing authentication
def test_missing_authentication():
    response = client.get("/api/v1/ingredients/")
    assert response.status_code == 401  # Assuming 401 is returned for missing authentication
