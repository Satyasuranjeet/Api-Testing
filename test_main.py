import pytest
from fastapi.testclient import TestClient
from main import app, students_collection
from bson import ObjectId

client = TestClient(app)

# Sample test student
test_student = {
    "name": "Test Student",
    "age": 21,
    "university": "Test University"
}

# Fixture for inserting and cleaning up test student
@pytest.fixture
def setup_student():
    inserted = students_collection.insert_one(test_student.copy())
    student_id = str(inserted.inserted_id)
    yield student_id
    students_collection.delete_one({"_id": ObjectId(student_id)})

def test_create_student():
    response = client.post("/students/", json=test_student)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == test_student["name"]
    students_collection.delete_one({"_id": ObjectId(data["id"])})

def test_get_all_students():
    response = client.get("/students/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_student_valid(setup_student):
    response = client.get(f"/students/{setup_student}")
    assert response.status_code == 200
    assert response.json()["name"] == test_student["name"]

def test_get_single_student_invalid():
    response = client.get("/students/605c5f3b4f1a256d8f1a9999")  # fake ObjectId
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"

def test_update_student_valid(setup_student):
    updated_data = {"name": "Updated Name", "age": 25, "university": "Updated Uni"}
    response = client.put(f"/students/{setup_student}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

def test_update_student_invalid():
    response = client.put("/students/605c5f3b4f1a256d8f1a9999", json=test_student)
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"

def test_delete_student_valid():
    inserted = students_collection.insert_one(test_student.copy())
    student_id = str(inserted.inserted_id)
    response = client.delete(f"/students/{student_id}")
    assert response.status_code == 200
    assert f"Student {student_id} deleted successfully" in response.json()["message"]

def test_delete_student_invalid():
    response = client.delete("/students/605c5f3b4f1a256d8f1a9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"
