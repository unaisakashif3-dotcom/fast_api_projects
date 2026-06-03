from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Task Manager API")

# Pydantic model
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = FalseR

# Fake database
tasks_db = []
task_counter = 1

# CREATE
@app.post("/tasks/", response_model=dict)
def create_task(task: Task):
    global task_counter
    new_task = task.dict()
    new_task["id"] = task_counter
    tasks_db.append(new_task)
    task_counter += 1
    return {"message": "Task created!", "task": new_task}

# READ all
@app.get("/tasks/", response_model=List[dict])
def get_all_tasks():
    return tasks_db

# READ one
@app.get("/tasks/{task_id}")
def get_one_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return {"found": True, "task": task}
    return {"found": False, "message": f"Task {task_id} not found"}

# UPDATE
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db[index] = {
                "id": task_id,
                "title": updated_task.title,
                "description": updated_task.description,
                "completed": updated_task.completed
            }
            return {"message": "Task updated!", "task": tasks_db[index]}
    return {"error": f"Task {task_id} not found"}

# DELETE
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks_db
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            deleted = tasks_db.pop(index)
            return {"message": "Task deleted!", "deleted_task": deleted}
    return {"error": f"Task {task_id} not found"}

#get all tasks by completion status
@app.get("/tasks/")
def get_all_tasks(completed: Optional[bool] = None):
    if completed is not None:
        return [task for task in tasks_db if task["completed"] == completed]
    return tasks_db

#delete all completed tasks
@app.delete("/tasks/clear/completed")
def delete_completed_tasks():
    global tasks_db
    tasks_db = [task for task in tasks_db if not task["completed"]]
    return {"message": "All completed tasks deleted"}