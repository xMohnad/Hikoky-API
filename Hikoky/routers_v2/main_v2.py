from fastapi import FastAPI
from . import home, manga, chapter


app_v2 = FastAPI(
    title="Manga Scraper API",
    description="API to scrape manga information from different sources",
    version="2.0.0"
)

app_v2.include_router(home.router)
app_v2.include_router(manga.router)
app_v2.include_router(chapter.router)

