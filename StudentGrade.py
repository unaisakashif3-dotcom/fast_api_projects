from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from statistics import mean  

app = FastAPI(title="Student Grade Tracker API")

# Model for Student Grade
class Grade(BaseModel):
    subject: str = Field(..., min_length=4, max_length=50, description="Subject name")
    score: float = Field(..., ge=0, le=100, description="Grade score")
    date: Optional[str] = Field(None, description="Date of the grade")

class Student(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Student's name")
    student_id: str = Field(..., pattern="^[F|S]\\d{8}$", description="Student's ID")
    
class StudentGrade(Student):
    grades: List[Grade] = Field(default_factory=list, description="List of grades for the student")
    average_grade: Optional[float] = Field(None, description="Average grade for the student")

# Fake database
students_db: dict[str, StudentGrade] = {}
student_counter = 1

# ========== CREATE ==========
@app.post("/students/", status_code=201)    
def add_student(student: Student):
    global student_counter
    
    # Check for duplicate student_id
    for existing_student in students_db.values():
        if existing_student.student_id == student.student_id:
            raise HTTPException(status_code=400, detail="Student ID already exists")
    
    new_student = StudentGrade(**student.model_dump())
    new_student.average_grade = None
    students_db[str(student_counter)] = new_student
    student_counter += 1
    
    return {
        "message": "Student added!",
        "student_count": student_counter - 1,
        "student": new_student
    }  

# ========== ADD GRADE ==========
@app.post("/students/{student_id}/grades/", status_code=201)
def add_grade(student_id: str, grade: Grade):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    student.grades.append(grade)
    
    # Recalculate average grade
    if student.grades:
        student.average_grade = round(mean(g.score for g in student.grades), 2)
    else:
        student.average_grade = None
    
    return {
        "message": "Grade added!",
        "student_id": student_id,
        "grade": grade,
        "average_grade": student.average_grade
    }

# ========== READ (with search) ==========
@app.get("/students/")
def get_all_students():
    # Convert to dict with string IDs for JSON serialization
    students_with_ids = {}
    for student_id, student in students_db.items():
        students_with_ids[student_id] = {
            "name": student.name,
            "student_id": student.student_id,
            "grades": student.grades,
            "average_grade": student.average_grade
        }
    
    return {
        "total": len(students_db),
        "students": students_with_ids
    }

# ========== READ ONE STUDENT ==========
@app.get("/students/{student_id}")  
def get_student(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    
    # Add statistics if grades exist
    if student.grades:
        scores = [g.score for g in student.grades]
        student.average_grade = round(mean(scores), 2)  # Update average
        
        # Add extra stats (not stored in model)
        return {
            "id": student_id,
            "name": student.name,
            "student_id": student.student_id,
            "grades": student.grades,
            "average_grade": student.average_grade,
            "stats": {
                "highest": max(scores),
                "lowest": min(scores),
                "total_grades": len(scores)
            }
        }
    
    return {
        "id": student_id,
        "name": student.name,
        "student_id": student.student_id,
        "grades": student.grades,
        "average_grade": student.average_grade
    }

# ========== UPDATE student info ==========
@app.put("/students/{student_id}")  
def update_student(student_id: str, updated_info: Student):
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if new student_id conflicts with existing one
    if updated_info.student_id != students_db[student_id].student_id:
        for existing_student in students_db.values():
            if existing_student.student_id == updated_info.student_id:
                raise HTTPException(status_code=400, detail="Student ID already exists")
    
    existing_grades = students_db[student_id].grades
    student = students_db[student_id]

    student.name = updated_info.name
    student.student_id = updated_info.student_id
    student.grades = existing_grades
    
    return {
        "message": "Student information updated!",
        "student": student
    }

# ========== DELETE student ==========
@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    students_db.pop(student_id)
    
    return {
        "message": "Student deleted successfully!"
    }

# ========== DELETE specific grade ==========
@app.delete("/students/{student_id}/grades/{grade_index}")
def delete_grade(student_id: str, grade_index: int):
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    
    if grade_index < 0 or grade_index >= len(student.grades):
        raise HTTPException(status_code=404, detail="Grade not found")
    
    deleted_grade = student.grades.pop(grade_index)
    
    # Recalculate average grade after deletion
    if student.grades:
        student.average_grade = round(mean(g.score for g in student.grades), 2)
    else:
        student.average_grade = None
    
    return {
        "message": "Grade deleted successfully!",
        "deleted_grade": deleted_grade,
        "average_grade": student.average_grade
    }