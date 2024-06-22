
from typing import Optional, Tuple, Dict, Any


from fastapi import APIRouter, Depends, HTTPException, Query
from ..dependencies import get_handler, fetch_data

router = APIRouter(
    tags=["Manga"],
    responses={404: {"description": "Not found"}}
)

@router.get("/manga", summary="Get Manga Page", response_description="Manga page data for the specified source.")
async def manga(
    manga_URl: str = Query(None, title="Manga page URL", description="URL for the manga page."), 
    handler: Dict[str, Any] = Depends(get_handler)

):
    """
    Retrieve the manga page data for the specified source.

    Args:
        source (str): The name of the source.
        mangaUrl (Optional[str], optional): URL for the manga page. Defaults to None.

    Returns:
        dict: Success status, source name, and data from the manga page.
    """
    
    result = await fetch_data(mangaUrl)
    results = handler["manga_page"](result)
    
    return {'success': True, "source": source, "data": [results]}
