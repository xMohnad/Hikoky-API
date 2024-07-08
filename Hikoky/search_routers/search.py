from fastapi import APIRouter, HTTPException
from ..dependencies.search import handle_search, handle_search_in_all_sources

router = APIRouter(
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    summary="Search in Source or All Sources",
    response_description="Search results for the specified source or all sources.",
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

    if source:
        results = await handle_search(keyword, source)
        return {"success": True, "source": source, "data": results}
    else:
        results = await handle_search_in_all_sources(keyword)
        return {"data": results}
