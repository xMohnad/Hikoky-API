from fastapi import APIRouter, HTTPException

from ..dependencies import load_source, list_sources
from typing import Dict, Any, List


async def search_in_source(keyword, source):
    source = await load_source(source)
    return await source.search(keyword)


async def search_in_all_sources(keyword: str) -> List[Dict[str, Any]]:
    results = []
    sources = await list_sources()
    for source in sources:
        try:
            source = await load_source(source)
            search_result = await source.search(keyword)
            results.append({"data": search_result})

        except HTTPException as e:
            results.append({"status_code": e.status_code, "error": e.detail})

    if not results:
        raise HTTPException(status_code=404, detail=results)
    return results


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
        results = await search_in_source(keyword=keyword, source=source)
        return {"success": True, "data": results}
    else:
        results = await search_in_all_sources(keyword)
        return {"results": results}
