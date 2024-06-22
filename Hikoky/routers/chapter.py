from fastapi import APIRouter, HTTPException
from fastapi import FastAPI, Query, Depends
from typing import Optional, Tuple, Dict, Any
from ..dependencies import get_handler, fetch_data


router = APIRouter(
    tags=["Manga"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{source}/chapter", summary="Get Chapter Page", response_description="Chapter page data for the specified source.")
async def chapter(source: str, chapterUrl: Optional[str] = Query(None, title="Chapter page URL", description="URL for the chapter page."), 
        handler: Dict[str, Any] = Depends(get_handler)):
    """
    Retrieve the chapter page data for the specified source.

    Args:
        source (str): The name of the source.
        chapterUrl (Optional[str], optional): URL for the chapter page. Defaults to None.

    Returns:
        dict: Success status, source name, and data from the chapter page.
    """
    
    result = await fetch_data(chapterUrl)
    results = handler["chapter_page"](result, chapterUrl)

    return {'success': True, "source": source, "data": results}
