from fastapi import APIRouter, Query
from typing import Optional
from ..dependencies import get_handler, fetch_data
from fastapi import HTTPException

# إنشاء APIRouter مع إعدادات الوسوم والاستجابات المخصصة
router = APIRouter(
    tags=["Manga"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/chapter", 
    # response_model=ChapterModel,
    summary="Get Chapter Page", 
    response_description="Chapter page data for the specified source."
)
async def chapter(
    chapterURL: str = Query(
        ..., 
        title="Chapter Page URL", 
        description="URL for the chapter page. Provide this URL to fetch the chapter page data."
    )
):
    """
    Retrieve the chapter page data for the specified source.

    Parameters:
    - chapterURL (str): The URL for the chapter page. This parameter is required to fetch the chapter page data.

    Returns:
    - dict: A dictionary containing:
        - success (bool): Indicates if the operation was successful.
        - source (str): The name of the source.
        - data (dict): The data fetched from the chapter page.
    """
    try:
        url, handler = await get_handler(chapterURL)
        result = await fetch_data(url)
        results = handler["chapter_page"](result, url)
    
        return {'success': True, "source": handler["name"], "data": results}
    
    except HTTPException as e:
        return {"success": False, **e.detail}

    except Exception as e:
        return {"success": False, "error": str(e)}


