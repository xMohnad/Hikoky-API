from fastapi import FastAPI
from .routers_v1.main_v1 import app_v1
from .routers_v2.main_v2 import app_v2
import json
from .search_routers.search import router as search_in_sources

servers = [
    {"url": "/", "description": "Get Available Sources"},
    {"url": "/v1", "description": "First Edition (V1)"},
    {"url": "/v2", "description": "Second Edition (V2)"},
]

app = FastAPI(
    title="Manga Scraper API",
    description=(
        "## Overview\n"
        "This API allows you to scrape manga information from various sources.\n\n"
        "## Available Versions:\n"
        "- **[First Edition (V1) Documentation](/v1/docs)**: Use links as queries to fetch data.\n"
        "- **[Second Edition (V2) Documentation](/v2/docs)**: Endpoints organized by manga name and chapter number.\n"
        "## How to Use:\n"
        "### Version 1:\n"
        "Fetch data using direct links. Refer to the [documentation](/v1/docs) for more details.\n\n"
        "### Version 2:\n"
        "Endpoints are organized by manga name and chapter number (e.g., `/mangaPath/chapterNumber`).\n\n"
        "## Contact\n"
        "For support or further information, you can contact us through our [Twitter](https://x.com/xMohnad13?t=mRA6tFAcs32yfNjPPX5XTQ&s=09).\n"
    ),
    version="2.0.0",
    servers=servers,
    contact={
        "name": "API Support",
        "twitter": "https://x.com/xMohnad13?t=mRA6tFAcs32yfNjPPX5XTQ&s=09",
    },
)


@app.get(
    "/",
    tags=["Sources"],
    summary="Get Available Sources",
    response_description="List of available sources.",
    description=(
        "### Retrieve the list of available manga sources.\n\n"
        "This endpoint returns a list of available manga sources, each with its details such as base URL, logo URL, name, "
        "and endpoints for version 1 and version 2 of the API.\n\n"
    ),
)
async def list_sources():
    with open("index.json") as f:
        return json.load(f)


app.include_router(search_in_sources, prefix="/search")


app.mount("/v1", app_v1)
app.mount("/v2", app_v2)
