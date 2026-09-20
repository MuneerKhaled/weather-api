from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Weather API")

# Get API key from .env
API_KEY = os.getenv("API_KEY")

# Store tasks
tasks = []

# Serve frontend files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


# -------------------------
# Frontend
# -------------------------

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# -------------------------
# Weather API
# -------------------------

@app.get("/weather/{city}")
async def weather(city: str):

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API_KEY is missing from .env"
        )

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    data = response.json()

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["main"]
    }


# -------------------------
# Task Model
# -------------------------

class Task(BaseModel):
    title: str
    description: str
    category: str = "daily"
    status: str = "pending"


# -------------------------
# Create Task
# -------------------------

@app.post("/tasks")
def create_task(task: Task):

    new_task = task.model_dump()

    new_task["id"] = len(tasks) + 1

    tasks.append(new_task)

    return new_task


# -------------------------
# Get All Tasks
# -------------------------

@app.get("/tasks")
def get_tasks():

    return tasks


# -------------------------
# Get One Task
# -------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    for task in tasks:

        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )


# -------------------------
# Update Task
# -------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):

    for old_task in tasks:

        if old_task["id"] == task_id:

            old_task.update(task.model_dump())

            return old_task

    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )


# -------------------------
# Delete Task
# -------------------------

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    for task in tasks:

        if task["id"] == task_id:

            tasks.remove(task)

            return {
                "message": "Task deleted"
            }

    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )