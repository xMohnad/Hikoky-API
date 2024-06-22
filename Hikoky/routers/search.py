from fastapi import APIRouter, Depends
from fastapi import Query
from typing import Optional, Dict, Any
from config import searchHandlers
from ..dependencies import getHandlerAndCheckErrors, fetch_data
from Hikoky.models import Search


router = APIRouter(
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)

@router.get("/search", summary="Search in Source", response_description="Search results for the specified source.")
async def search(source: str, query: str = Query(..., title="Search Query", description="Search term."),
                handler: Dict[str, Any] = Depends(getHandlerAndCheckErrors)):
    """
    Search for a term in the specified source.

    Args:
        source (str): The name of the source.
        query (str): The search query.

    Returns:
        dict: Success status, source name, and search results.
    """
    handler = searchHandlers.get(source)
    if not handler:
        return {'success': False, 'error': 'Invalid source'}

    url = handler["searchUrl"]
    method = handler["method"]
    headers = handler["headers"]
    params = handler.get("params")(query) if handler.get("params") else None
    data = handler.get("data")(query) if handler.get("data") else None
    parse = handler["parse"]
    
    result = await fetch_data(url, method, headers=headers, params=params, data=data, parse=parse)

    return await handler["search"](result, source)

@router.get("/search/all")
async def get_all_search_data():



    return Search.get_all_data()
