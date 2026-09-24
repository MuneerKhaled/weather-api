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


# Store books
books = []


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
async def get_weather(city: str):

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
# Book Model
# -------------------------

class Book(BaseModel):
    title: str
    author: str
    category: str = "general"
    status: str = "available"


# -------------------------
# Create Book
# -------------------------

@app.post("/books")
def create_book(book: Book):

    new_book = book.model_dump()

    new_book["id"] = len(books) + 1

    books.append(new_book)

    return new_book


# -------------------------
# Get All Books
# -------------------------

@app.get("/books")
def get_books():

    return books


# -------------------------
# Get One Book
# -------------------------

@app.get("/books/{book_id}")
def get_book(book_id: int):

    for book in books:

        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# -------------------------
# Update Book
# -------------------------

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):

    for old_book in books:

        if old_book["id"] == book_id:

            old_book.update(book.model_dump())

            return old_book

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )


# -------------------------
# Delete Book
# -------------------------

@app.delete("/books/{book_id}")
def delete_book(book_id: int):

    for book in books:

        if book["id"] == book_id:

            books.remove(book)

            return {
                "message": "Book deleted"
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found"
    )