from fastapi import APIRouter, Depends, Query
from typing import Dict, Any
from ..dependencies import handle_search

# إنشاء APIRouter مع إعدادات الوسوم والاستجابات المخصصة
router = APIRouter(
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/search", 
    summary="Search in Source", 
    response_description="Search results for the specified source."
)
async def search(
    result: Dict[str, Any] = Depends(handle_search)
):
    """
    Search for a term in the specified source.

    Parameters:
    - result (Dict[str, Any]): The result of the search, fetched using the handle_search dependency. This dictionary contains the search results.

    Returns:
    - dict: A dictionary containing:
        - success (bool): Indicates if the operation was successful.
        - source (str): The name of the source.
        - data (list): The search results.
    """
    return result


from Hikoky.models import Search
@router.get("/search/all")
async def get_all_search_data():



    return Search.get_all_data()
