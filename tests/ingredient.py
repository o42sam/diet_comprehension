import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from app.main import app
from app.models.ingredient import Ingredient, IngredientCreate
from app.exceptions.ingredient import (
    IngredientCreationError,
    IngredientAlreadyExistsError,
    IngredientSearchError,
    IngredientRetrievalError
)
from app.dependencies.auth import get_current_user
# Import ANY from unittest.mock
from unittest.mock import patch, MagicMock, ANY

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

# Create a mock Ingredient object for service layer return simulation
mock_created_ingredient = Ingredient(
    _id=mock_ingredient_data["_id"], # Use _id for initialization due to alias
    name=mock_ingredient_data["name"],
    description=mock_ingredient_data["description"],
    quantity=mock_ingredient_data["quantity"],
    unit=mock_ingredient_data["unit"],
    reference_quantity=mock_ingredient_data["reference_quantity"],
    reference_unit=mock_ingredient_data["reference_unit"],
    nutrients=mock_ingredient_data["nutrients"]
)

mock_ingredient_list_data = [
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

# Convert list data to list of Ingredient models for mocking service return
mock_ingredient_list = [Ingredient.model_validate(ing) for ing in mock_ingredient_list_data]

mock_search_results_data = [
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
# Convert search data to list of Ingredient models
mock_search_results = [Ingredient.model_validate(ing) for ing in mock_search_results_data]


# Fixture to override authentication dependency
@pytest.fixture
def override_auth():
    async def mock_get_current_user():
        return "test_user_id"
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    # Clean up overrides after test
    app.dependency_overrides.pop(get_current_user, None)

# Test creating a new ingredient - success case
@pytest.mark.asyncio
async def test_create_ingredient_success(override_auth):
    # Mock the service layer function instead of the repository layer
    with patch("app.api.v1.ingredient.create_ingredient", return_value=mock_created_ingredient) as mock_service_create:
        request_payload = {
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
        response = client.post(
            "/api/v1/ingredients/",
            json=request_payload
        )
        # Assert service was awaited correctly (expecting db object and IngredientCreate model)
        mock_service_create.assert_awaited_once()
        call_args, call_kwargs = mock_service_create.call_args
        # Check positional args (should contain db object - use ANY)
        assert len(call_args) == 2
        assert call_args[0] == ANY # Check that the first arg (db) was passed
        # Check the second positional arg (ingredient data)
        assert isinstance(call_args[1], IngredientCreate)
        assert call_args[1].name == request_payload["name"]
        # Check keyword args (should be empty)
        assert not call_kwargs

        # Assert response
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Chicken Breast"
        assert data["_id"] == mock_ingredient_data["_id"]
        assert data["description"] == mock_ingredient_data["description"]

# Test creating a new ingredient - already exists
@pytest.mark.asyncio
async def test_create_ingredient_already_exists(override_auth):
     # Mock the service layer function raising the specific exception
    with patch("app.api.v1.ingredient.create_ingredient",
               side_effect=IngredientAlreadyExistsError("Ingredient with name 'Chicken Breast' already exists")) as mock_service_create:
        request_payload = {
            "name": "Chicken Breast",
            "description": "Boneless, skinless chicken breast",
            "quantity": 100.0,
            "unit": 1.0,
            "reference_quantity": 100.0,
            "reference_unit": "g",
            "nutrients": { "protein": 31.0, "fat": 3.6, "carbohydrates": 0.0, "calories": 165.0 }
        }
        response = client.post(
            "/api/v1/ingredients/",
            json=request_payload
        )
        # Ensure the mock was CALLED, even though it raised an exception
        mock_service_create.assert_called_once()
        call_args, _ = mock_service_create.call_args
        assert call_args[0] == ANY # db object
        assert isinstance(call_args[1], IngredientCreate) # ingredient data
        assert call_args[1].name == request_payload["name"]

        # Assert response status and detail
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

# Test creating a new ingredient - database error (via service layer)
@pytest.mark.asyncio
async def test_create_ingredient_database_error(override_auth):
     # Mock the service layer function raising the specific exception
    with patch("app.api.v1.ingredient.create_ingredient",
               side_effect=IngredientCreationError("Failed to create ingredient due to a database error")) as mock_service_create:
        request_payload = {
            "name": "Chicken Breast",
            "description": "Boneless, skinless chicken breast",
            "quantity": 100.0,
            "unit": 1.0,
            "reference_quantity": 100.0,
            "reference_unit": "g",
            "nutrients": { "protein": 31.0, "fat": 3.6, "carbohydrates": 0.0, "calories": 165.0 }
        }
        response = client.post(
            "/api/v1/ingredients/",
            json=request_payload
        )
        # Ensure the mock was CALLED, even though it raised an exception
        mock_service_create.assert_called_once()
        call_args, _ = mock_service_create.call_args
        assert call_args[0] == ANY # db object
        assert isinstance(call_args[1], IngredientCreate) # ingredient data
        assert call_args[1].name == request_payload["name"]

        # Assert response status and detail
        assert response.status_code == 500
        assert "Failed to create ingredient" in response.json()["detail"]

# Test listing all ingredients - success case
@pytest.mark.asyncio
async def test_list_ingredients_success(override_auth):
     # Mock the service layer function
    with patch("app.api.v1.ingredient.get_ingredients", return_value=mock_ingredient_list) as mock_service_get:
        response = client.get("/api/v1/ingredients/")

        mock_service_get.assert_awaited_once_with(ANY)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["_id"] == mock_ingredient_list_data[0]["_id"]
        assert data[0]["name"] == mock_ingredient_list_data[0]["name"]
        assert data[1]["_id"] == mock_ingredient_list_data[1]["_id"]
        assert data[1]["name"] == mock_ingredient_list_data[1]["name"]


# Test listing all ingredients - database error (via service layer)
@pytest.mark.asyncio
async def test_list_ingredients_database_error(override_auth):
    # Mock the service layer function raising the specific exception
    with patch("app.api.v1.ingredient.get_ingredients",
               side_effect=IngredientRetrievalError("Failed to retrieve ingredients due to a database error")) as mock_service_get:
        response = client.get("/api/v1/ingredients/")
        # Use assert_called_once_with for side_effect exceptions
        mock_service_get.assert_called_once_with(ANY)
        assert response.status_code == 500
        assert "Failed to retrieve ingredients" in response.json()["detail"]

# Test searching ingredients - success case
@pytest.mark.asyncio
async def test_search_ingredients_success(override_auth):
    # Mock the service layer function
    with patch("app.api.v1.ingredient.search_ingredients", return_value=mock_search_results) as mock_service_search:
        response = client.get("/api/v1/ingredients/search?query=chicken")

        mock_service_search.assert_awaited_once_with(ANY, query="chicken")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["_id"] == mock_search_results_data[0]["_id"]
        assert data[0]["name"] == mock_search_results_data[0]["name"]

# Test searching ingredients - empty results
@pytest.mark.asyncio
async def test_search_ingredients_empty_results(override_auth):
     # Mock the service layer function
    with patch("app.api.v1.ingredient.search_ingredients", return_value=[]) as mock_service_search:
        response = client.get("/api/v1/ingredients/search?query=nonexistent")

        mock_service_search.assert_awaited_once_with(ANY, query="nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

# Test searching ingredients - database error (via service layer)
@pytest.mark.asyncio
async def test_search_ingredients_database_error(override_auth):
    # Mock the service layer function raising the specific exception
    with patch("app.api.v1.ingredient.search_ingredients",
               side_effect=IngredientSearchError("Failed to search ingredients due to a database error")) as mock_service_search:
        response = client.get("/api/v1/ingredients/search?query=chicken")
        # Use assert_called_once_with for side_effect exceptions
        mock_service_search.assert_called_once_with(ANY, query="chicken")
        assert response.status_code == 500
        assert "Failed to search ingredients" in response.json()["detail"]

# Test missing authentication
def test_missing_authentication():
    if get_current_user in app.dependency_overrides:
         app.dependency_overrides.pop(get_current_user)

    response_get = client.get("/api/v1/ingredients/")
    assert response_get.status_code == 401

    # Add minimal required fields for IngredientCreate to pass validation if necessary
    # Or use {} if validation is bypassed before auth check
    response_post = client.post("/api/v1/ingredients/", json={
        "name": "Test", "quantity": 1, "unit": 1,
        "reference_quantity": 1, "reference_unit": "g", "nutrients": {}
    })
    assert response_post.status_code == 401

    response_search = client.get("/api/v1/ingredients/search?query=a")
    assert response_search.status_code == 401