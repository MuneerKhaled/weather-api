from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os


# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="Weather & Notes API")


# OpenWeather API key
WEATHER_API_KEY = os.getenv("API_KEY")


# In-memory notes storage
notes = []


# Serve frontend
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# =========================
# Home
# =========================

@app.get("/")
def index():
    return FileResponse("frontend/index.html")


# =========================
# Weather
# =========================

@app.get("/api/weather")
async def get_weather(city: str):

    if not WEATHER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Weather API key is not configured"
        )

    weather_url = "https://api.openweathermap.org/data/2.5/weather"

    query = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:

        result = await client.get(
            weather_url,
            params=query
        )

    if result.status_code != 200:
        raise HTTPException(
            status_code=result.status_code,
            detail="Unable to retrieve weather information"
        )

    weather_data = result.json()

    return {
        "location": weather_data["name"],
        "temperature_celsius": weather_data["main"]["temp"],
        "feels_like": weather_data["main"]["feels_like"],
        "humidity": weather_data["main"]["humidity"],
        "weather": weather_data["weather"][0]["description"]
    }


# =========================
# Note Model
# =========================

class Note(BaseModel):
    title: str
    content: str
    priority: str = "normal"
    completed: bool = False


# =========================
# Create Note
# =========================

@app.post("/notes")
def add_note(note: Note):

    note_data = note.model_dump()

    note_data["id"] = len(notes) + 1

    notes.append(note_data)

    return {
        "message": "Note created successfully",
        "note": note_data
    }


# =========================
# Get All Notes
# =========================

@app.get("/notes")
def list_notes():

    return {
        "count": len(notes),
        "notes": notes
    }


# =========================
# Get Single Note
# =========================

@app.get("/notes/{note_id}")
def get_note(note_id: int):

    for note in notes:

        if note["id"] == note_id:
            return note

    raise HTTPException(
        status_code=404,
        detail="Note not found"
    )


# =========================
# Update Note
# =========================

@app.patch("/notes/{note_id}")
def edit_note(note_id: int, updated_note: Note):

    for note in notes:

        if note["id"] == note_id:

            note.update(updated_note.model_dump())

            return {
                "message": "Note updated successfully",
                "note": note
            }

    raise HTTPException(
        status_code=404,
        detail="Note not found"
    )


# =========================
# Delete Note
# =========================

@app.delete("/notes/{note_id}")
def remove_note(note_id: int):

    for index, note in enumerate(notes):

        if note["id"] == note_id:

            deleted_note = notes.pop(index)

            return {
                "message": "Note deleted successfully",
                "note": deleted_note
            }

    raise HTTPException(
        status_code=404,
        detail="Note not found"
    )
