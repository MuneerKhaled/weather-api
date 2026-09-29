from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

import httpx
import os


# ============================================================
# Environment Configuration
# ============================================================

load_dotenv()

API_KEY = os.getenv("API_KEY")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Book & Weather API",
    version="1.0.0",
    description="API for managing books and checking weather information.",
)


# ============================================================
# Temporary Book Storage
# ============================================================

book_list = []


# ============================================================
# Frontend Configuration
# ============================================================

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend",
)


@app.get("/")
def home() -> FileResponse:
    """
    Display the frontend application.
    """
    return FileResponse("frontend/index.html")


# ============================================================
# Weather API
# ============================================================

@app.get("/weather/{city}")
async def weather(city: str) -> dict:
    """
    Get current weather information for a city.
    """

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Weather API key is not configured.",
        )

    weather_url = (
        "https://api.openweathermap.org/data/2.5/weather"
    )

    parameters = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            weather_url,
            params=parameters,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Unable to retrieve weather information.",
        )

    weather_data = response.json()

    return {
        "city": weather_data["name"],
        "temperature": weather_data["main"]["temp"],
        "humidity": weather_data["main"]["humidity"],
        "condition": weather_data["weather"][0]["main"],
    }


# ============================================================
# Book Data Model
# ============================================================

class Book(BaseModel):
    """
    Schema used for creating and updating books.
    """

    title: str
    author: str
    category: str = "General"
    status: str = "Available"


# ============================================================
# CREATE - Add New Book
# ============================================================

@app.post("/books")
def add_book(book: Book) -> dict:
    """
    Add a new book to the collection.
    """

    book_data = book.model_dump()

    book_data["id"] = len(book_list) + 1

    book_list.append(book_data)

    return {
        "message": "Book added successfully",
        "book": book_data,
    }


# ============================================================
# READ - Get All Books
# ============================================================

@app.get("/books")
def get_all_books() -> list:
    """
    Return all books in the collection.
    """

    return book_list


# ============================================================
# READ - Get Book By ID
# ============================================================

@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict:
    """
    Find a book using its ID.
    """

    for book in book_list:
        if book["id"] == book_id:
            return book

    raise HTTPException(
        status_code=404,
        detail="Book not found.",
    )


# ============================================================
# UPDATE - Modify Existing Book
# ============================================================

@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book) -> dict:
    """
    Update an existing book.
    """

    for book in book_list:

        if book["id"] == book_id:

            book.update(updated_book.model_dump())

            return {
                "message": "Book updated successfully",
                "book": book,
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found.",
    )


# ============================================================
# DELETE - Remove Book
# ============================================================

@app.delete("/books/{book_id}")
def remove_book(book_id: int) -> dict:
    """
    Delete a book using its ID.
    """

    for book in book_list:

        if book["id"] == book_id:

            book_list.remove(book)

            return {
                "message": "Book deleted successfully",
            }

    raise HTTPException(
        status_code=404,
        detail="Book not found.",
    )