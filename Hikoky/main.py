from fastapi import FastAPI
from config import get_sources
from .routers_v1.main_v1 import app_v1
from .routers_v2.main_v2 import app_v2
from .search_routers.main_search import search
import json

servers = [
    {"url": "/", "description": "Get Available Sources"},
    {"url": "/v1", "description": "First Edition (V1)"},
    {"url": "/v2", "description": "Second Edition (V2)"},
    {"url": "/search", "description": "Search Endpoint"},
]

app = FastAPI(
    title="Manga Scraper API",
    description=(
        "## Overview\n"
        "This API allows you to scrape manga information from various sources.\n\n"
        "## Available Versions:\n"
        "- **[First Edition (V1) Documentation](/v1/docs)**: Use links as queries to fetch data.\n"
        "- **[Second Edition (V2) Documentation](/v2/docs)**: Endpoints organized by manga name and chapter number.\n"
        "- **[Search Endpoint](/search/docs)**: Search manga across different sources.\n\n"
        "## How to Use:\n"
        "### Version 1:\n"
        "Fetch data using direct links. Refer to the [documentation](/v1/docs) for more details.\n\n"
        "### Version 2:\n"
        "Endpoints are organized by manga name and chapter number (e.g., `/mangaPath/chapterNumber`).\n\n"
        "### Search Endpoint:\n"
        "Search for manga across various sources using this endpoint. Refer to the [documentation](/search/docs) for more details.\n\n"
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


app.mount("/v1", app_v1)
app.mount("/v2", app_v2)
app.mount("/search", search)
