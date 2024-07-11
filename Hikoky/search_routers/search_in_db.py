from fastapi import APIRouter
from Hikoky.models import Search
from typing import Optional

router = APIRouter(
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/db/search",
    summary="Search in Database",
    response_description="A list of search results matching the keyword.",
)
async def search_in_source_or_all_sources_in_database(
    keyword: str, source: Optional[str] = None
):
    """
    Search for a specific keyword in a specified source or across all sources in the database.
    """
    results = Search.perform_search(source, keyword)
    return results


@router.get("/db/all")
async def get_all_search_in_database():
    """
    Retrieve all search entries from the database.
    """
    return Search.get_all_data()
