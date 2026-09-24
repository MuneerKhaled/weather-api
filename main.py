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
app = FastAPI(title="Book and Weather API")


# Get API key from .env
API_KEY = os.getenv("API_KEY")


# Book model
class Book(BaseModel):
    title: str
    author: str
    year: int


# Home route
@app.get("/")
def home():
    return {"message": "Book and Weather API is running"}


# Get books
@app.get("/books")
def get_books():
    return {
        "books": [
            {
                "title": "The Alchemist",
                "author": "Paulo Coelho",
                "year": 1988
            },
            {
                "title": "1984",
                "author": "George Orwell",
                "year": 1949
            }
        ]
    }


# Create a book
@app.post("/books")
def create_book(book: Book):
    return {
        "message": "Book created successfully",
        "book": book
    }


# Weather route
@app.get("/weather/{city}")
async def get_weather(city: str):

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key is missing"
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
            detail="Could not get weather data"
        )

    data = response.json()

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"]
    }