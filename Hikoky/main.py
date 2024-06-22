from fastapi import FastAPI
from fastapi import APIRouter
from .routers import home, manga, chapter, search

from config import get_sources


app = FastAPI(
    title="Manga Scraper API",
    description="API to scrape manga information from different sources",
    version="1.0.0"
)

@app.get("/", tags=["Manga"], summary="Get Available Sources", response_description="List of available sources.")
async def list_sources():
    """
    Retrieve the list of available manga sources.

    Returns:
        dict: Success status and data containing the list of sources.
    """
    return {'success': True, "data": get_sources()}

app.include_router(home.router)
app.include_router(manga.router)
app.include_router(chapter.router)
app.include_router(search.router)