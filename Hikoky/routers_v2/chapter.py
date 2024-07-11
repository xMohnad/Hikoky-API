from fastapi import APIRouter
from ..dependencies import handle_manga_chapter

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/source/{source}/{mangaPath}/{chapterPath}",
    tags=["Chapter"],
    summary="Retrieve Chapter Data",
    response_description="Successful Response with Chapter Data",
    description=(
        "**Retrieve the chapter data for a specified source, manga path, and chapter path.**"
    ),
)
async def read_chapter_path(source: str, mangaPath: str, chapterPath: str):
    """
    Retrieve the chapter data for a specified source, manga path, and chapter path.

    Args:
    - source (str): The source name.
    - mangaPath (str): The path to the manga.
    - chapterPath (str): The path to the chapter.

    Returns:
    - Dict[str, Any]: A dictionary with the success status, source name, and the chapter data.
    """
    return await handle_manga_chapter(source, mangaPath, chapterPath)


# from ..models.paths import PathChapter
# @router.get(
#     "/all/",
#     tags=["Chapter"],
# )
# async def all_data():

#     return PathChapter.get_all_data()
