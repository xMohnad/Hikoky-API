from fastapi import HTTPException
from Hikoky.dependencies.dependencies import fetch_data, get_handler_url

from .dependencies import err


async def handle_manchap(manga_url, chapter=False):
    handler = await get_handler_url(manga_url)

    if not handler:
        raise HTTPException(
            status_code=404, detail={**err, "error": "A valid URL must be provided."}
        )

    result = await fetch_data(manga_url)

    if chapter:
        results = handler["chapter_page"](
            result, manga_url, source=handler["name"], v1=True
        )

    elif not chapter:
        results = handler["manga_page"](result, source=handler["name"], v1=True)

    return {"success": True, "source": handler["name"], "data": results}
