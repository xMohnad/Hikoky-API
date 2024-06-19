from fastapi import FastAPI, Query
from typing import Optional, Tuple, Dict, Any
from PyProbe import pyparse

from config import sources, sourceHandlers

app = FastAPI(
    title="Manga Scraper API",
    description="API to scrape manga information from different sources",
    version="1.0.0"
)



def getHandlerAndCheckErrors(source: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
    """
    Retrieve the handler for the given source and check for errors.

    Args:
        source (str): The name of the source.

    Returns:
        Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]: Handler and error response if any.
    """
    handler = sourceHandlers.get(source)
    if not handler:
        return None, {'success': False, "error": "source not found"}
    return handler, None

@app.get("/", summary="Get Available Sources", response_description="List of available sources.")
async def get_sources():
    """
    Retrieve the list of available manga sources.

    Returns:
        dict: Success status and data containing the list of sources.
    """
    return {'success': True, "data": sources}

@app.get("/{source}", summary="Get Source Home Page", response_description="Home page data for the specified source.")
async def home(source: str, nextPageUrl: Optional[str] = Query(None, title="Next page URL", description="URL for the next page.")):
    """
    Retrieve the home page data for the specified source.

    Args:
        source (str): The name of the source.
        nextPageUrl (Optional[str], optional): URL for the next page. Defaults to None.

    Returns:
        dict: Success status, source name, and data from the home page.
    """
    handler, errorRes = getHandlerAndCheckErrors(source)
    if errorRes:
        return errorRes

    url = nextPageUrl or handler["url"]
    result = pyparse(url)
    if isinstance(result, dict) and 'error' in result:
        return {'success': False, "error": result['error']}

    results = handler["homePage"](result)
    
    return {'success': True, "source": source, "data": results}

@app.get("/{source}/manga", summary="Get Manga Page", response_description="Manga page data for the specified source.")
async def manga(source: str, mangaUrl: Optional[str] = Query(None, title="Manga page URL", description="URL for the manga page.")):
    """
    Retrieve the manga page data for the specified source.

    Args:
        source (str): The name of the source.
        mangaUrl (Optional[str], optional): URL for the manga page. Defaults to None.

    Returns:
        dict: Success status, source name, and data from the manga page.
    """
    handler, errorRes = getHandlerAndCheckErrors(source)
    if errorRes:
        return errorRes

    result = pyparse(mangaUrl)
    if isinstance(result, dict) and 'error' in result:
        return {'success': False, "error": result['error']}

    results = handler["mangaPage"](result)

    return {'success': True, "source": source, "data": [results]}

@app.get("/{source}/chapter", summary="Get Chapter Page", response_description="Chapter page data for the specified source.")
async def chapter(source: str, chapterUrl: Optional[str] = Query(None, title="Chapter page URL", description="URL for the chapter page.")):
    """
    Retrieve the chapter page data for the specified source.

    Args:
        source (str): The name of the source.
        chapterUrl (Optional[str], optional): URL for the chapter page. Defaults to None.

    Returns:
        dict: Success status, source name, and data from the chapter page.
    """
    handler, errorRes = getHandlerAndCheckErrors(source)
    if errorRes:
        return errorRes

    result = pyparse(chapterUrl)
    if isinstance(result, dict) and 'error' in result:
        return {'success': False, "error": result['error']}

    results = handler["chapterPage"](result, chapterUrl)

    return {'success': True, "source": source, "data": results}

@app.get("/{source}/search", summary="Search in Source", response_description="Search results for the specified source.")
async def search(source: str, query: str = Query(..., title="Search Query", description="Search term.")):
    """
    Search for a term in the specified source.

    Args:
        source (str): The name of the source.
        query (str): The search query.

    Returns:
        dict: Success status, source name, and search results.
    """
    handler, errorRes = getHandlerAndCheckErrors(source)
    if errorRes:
        return errorRes

    results = handler["search"](query, source)
    
    return results
