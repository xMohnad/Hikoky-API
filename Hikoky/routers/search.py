
from fastapi import APIRouter, HTTPException
from ..dependencies import handle_search, handle_search_in_all_sources

from Hikoky.models import Search
from typing import Optional

router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    summary="Search in Source or All Sources", 
    response_description="Search results for the specified source or all sources."
)
async def search(keyword: str, source: str = None) -> dict:
    """
    Search for a term in the specified source or in all sources.

    Parameters:
    - keyword (str): The search term.
    - source (str, optional): The name of the source to search in.

    Returns:
    - dict: A dictionary containing:
        - success (bool): Indicates if the operation was successful.
        - source (str, optional): The name of the source.
        - data (list): The search results.
    """

    try:
        if source:
            results = await handle_search(keyword, source)
            return {"success": True, "source": source, "data": results}
        else:
            results = await handle_search_in_all_sources(keyword)
            return {"success": True, "data": results}

    except HTTPException as e:
        return {"success": False, **e.detail}

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/db"
)
async def search_in_source_or_all_sources_in_database(keyword: str, source: Optional[str] = None):
    """
    Search for a specific keyword in a specified source or across all sources in the database.

    Args:
        keyword (str): The keyword to search for.
        source (Optional[str], optional): The source to search in. If not provided, the search will be across all sources. Defaults to None.

    Returns:
        List[SearchResult]: A list of search results matching the keyword.

    Raises:
        HTTPException: If no results are found.
    """

    try:
        results = Search.perform_search(source, keyword)
        return results

    except HTTPException as e:
        return {"success": False, **e.detail}

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/db/all"
)
async def get_all_search_in_database():
    """
    Retrieve all search entries from the database.

    Returns:
        List[SearchResult]: A list of all search entries in the database.
    """
    return Search.get_all_data()