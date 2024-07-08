from fastapi import FastAPI

from .search import router as search_in_sources
from .search_in_db import router as search_in_db

search = FastAPI(
    title="Manga Scraper API",
    description="API to search manga information from different sources",
    version="1.0.0",
)

search.include_router(search_in_sources)
search.include_router(search_in_db)
