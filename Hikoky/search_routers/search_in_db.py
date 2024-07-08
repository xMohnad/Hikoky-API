from fastapi import APIRouter, HTTPException
from Hikoky.models import Search
from typing import Optional

router = APIRouter(
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)


@router.get("/db")
async def search_in_source_or_all_sources_in_database(
    keyword: str, source: Optional[str] = None
):
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

    results = Search.perform_search(source, keyword)
    return results


@router.get("/db/all")
async def get_all_search_in_database():
    """
    Retrieve all search entries from the database.

    Returns:
        List[SearchResult]: A list of all search entries in the database.
    """
    return Search.get_all_data()
