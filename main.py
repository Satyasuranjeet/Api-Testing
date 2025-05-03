from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import List

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client setup
client = MongoClient("mongodb+srv://satya:satya@cluster0.8thgg4a.mongodb.net")
db = client["university"]
students_collection = db["students"]

# Pydantic models
class Student(BaseModel):
    name: str
    age: int
    university: str

class StudentResponse(Student):
    id: str

# Helper function to convert MongoDB ObjectId to string
def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "age": student["age"],
        "university": student["university"]
    }

# Create a new student
@app.post("/students/", response_model=StudentResponse)
async def create_student(student: Student):
    student_dict = student.dict()
    result = students_collection.insert_one(student_dict)
    student_dict["id"] = str(result.inserted_id)
    return student_dict

# Get all students
@app.get("/students/", response_model=List[StudentResponse])
async def get_students():
    students = students_collection.find()
    return [student_helper(student) for student in students]

# Get a single student by ID
@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str):
    student = students_collection.find_one({"_id": ObjectId(student_id)})
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_helper(student)

# Update an existing student by ID
@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: str, student: Student):
    updated_student = students_collection.find_one_and_update(
        {"_id": ObjectId(student_id)},
        {"$set": student.dict()},
        return_document=True
    )
    if updated_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_helper(updated_student)

# Delete a student by ID
@app.delete("/students/{student_id}", response_model=dict)
async def delete_student(student_id: str):
    deleted_student = students_collection.find_one_and_delete({"_id": ObjectId(student_id)})
    if deleted_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Student {student_id} deleted successfully"}
