from fastapi import APIRouter
from ..dependencies import handle_manga_request

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/{source}/{mangaPath}", tags=["Manga"], 
    summary="Retrieve Manga Data", 
    response_description="Successful Response with Manga Data",
    description=(
        "**Retrieve the manga data for a specified source and manga path.**"
    ),
)
async def read_manga_path(source: str, mangaPath: str):
    """
    Retrieve the manga data for a specified source and manga path.

    Args:
    - source (str): The source name.
    - mangaPath (str): The path to the manga.

    Returns:
    - Dict[str, Any]: A dictionary with the success status, source name, and the manga data.
    """
    return await handle_manga_request(source, mangaPath)
