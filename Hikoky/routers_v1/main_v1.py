from fastapi import FastAPI
from . import home, manga, chapter
from ..common_routers import next_home_page
from ..common_routers import next_manga_page

app_v1 = FastAPI(
    title="Manga Scraper API",
    description="API to scrape manga information from different sources",
    version="1.0.0",
)


app_v1.include_router(home.router)
app_v1.include_router(next_home_page.router)
app_v1.include_router(manga.router)
app_v1.include_router(next_manga_page.router)
app_v1.include_router(chapter.router)
