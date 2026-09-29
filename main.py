from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os


# ============================================================
# Environment Setup
# ============================================================

load_dotenv()

API_KEY = os.getenv("API_KEY")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Book & Weather API",
    description="API for managing books and checking weather",
    version="1.0.0"
)


# ============================================================
# Temporary Book Storage
# ============================================================

books = []


# ============================================================
# Frontend Configuration
# ============================================================

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


# ============================================================
# Home Page
# ============================================================

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# ============================================================
# Weather Endpoint
# ============================================================

@app.get("/weather/{city}")
async def weather(city: str):

    if API_KEY is None:
        raise HTTPException(
            status_code=500,
            detail="Weather API key is not configured"
        )

    weather_url = "https://api.openweathermap.org/data/2.5/weather"

    parameters = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        result = await client.get(
            weather_url,
            params=parameters
        )

    if result.status_code != 200:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.json()
        )

    weather_data = result.json()

    return {
        "city": weather_data["name"],
        "temperature": weather_data["main"]["temp"],
        "humidity": weather_data["main"]["humidity"],
        "condition": weather_data["weather"][0]["main"]
    }


# ============================================================
# Book Schema
# ============================================================

class Book(BaseModel):
    title: str
    author: str
    category: str = "General"
    status: str = "Available"


# ============================================================
# CREATE - Add New Book
# ============================================================

@app.post("/books")
def add_book(book: Book):

    book_data = book.model_dump()

    book_data["id"] = len(books) + 1

    books.append(book_data)

    return {
        "message": "Book added successfully",
        "book": book_data
    }


# ============================================================
# READ - Get All Books
# ============================================================

@app.get("/books")
def all_books():

    return {
        "total_books": len(books),
        "books": books
    }


# ============================================================
# READ - Get Book By ID
# ============================================================

@app.get("/books/{book_id}")
def find_book(book_id: int):

    for book in books:

        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=404,
        detail="Book with this ID was not found"
    )


# ============================================================
# UPDATE - Modify Book
# ============================================================

@app.put("/books/{book_id}")
def edit_book(book_id: int, book: Book):

    for existing_book in books:

        if existing_book["id"] == book_id:

            updated_data = book.model_dump()

            existing_book.update(updated_data)

            return {
                "message": "Book updated successfully",
                "book": existing_book
            }

    raise HTTPException(
        status_code=404,
        detail="Book with this ID was not found"
    )


# ============================================================
# DELETE - Remove Book
# ============================================================

@app.delete("/books/{book_id}")
def remove_book(book_id: int):

    for book in books:

        if book["id"] == book_id:

            books.remove(book)

            return {
                "message": "Book removed successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Book with this ID was not found"
    )