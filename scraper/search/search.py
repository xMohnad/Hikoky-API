import logging
from typing import Any, Dict, Union
from fastapi import HTTPException


async def notfound(source):
    return HTTPException(
        status_code=404,
        detail={
            "success": False,
            "Error": f"not found in {source}",
            "message": "لا توجد مانجا",
        },
    )


async def Failed_retrieve(source):
    return HTTPException(
        status_code=500,
        detail={"success": False, "error": f"Failed to retrieve data in {source}"},
    )


async def search3asq(
    response: Dict[str, Any], source: str
) -> Union[Dict[str, Any], Dict[str, str]]:
    if response.get("success", False):
        result = response.get("data", [])
        if result:
            data = []
            for manga in result:
                title = manga.get("title")
                link = manga.get("url")
                type_ = manga.get("type")
                data.append(
                    {
                        "title": title,
                        "link": link,
                        "cover": None,
                        "type": type_,
                        "badge": None,
                    }
                )
            return {"source": source, "data": data}
    else:
        error_data = response.get("data", [{}])[0]
        error_type = error_data.get("error", "Failed to retrieve data")
        if error_type == "not found":
            raise await notfound(source)
        else:
            logging.error(f"Failed to retrieve data in {source}")
            raise await Failed_retrieve(source)


async def search_teamx(response, source):
    if response:
        list_group = response.find("ol", class_="list-group")
        if list_group and list_group.find_all():
            results = response.find_all("li", class_="list-group-item")
            data = []
            for manga in results:
                title = manga.find("a", class_="fw-bold").text.strip()
                link = manga.find("a", class_="fw-bold")["href"]
                cover = manga.find("img")["src"] if manga.find("img") else None
                badge = (
                    manga.find("span", class_="badge").text.strip()
                    if manga.find("span", "badge")
                    else None
                )
                data.append(
                    {
                        "title": title,
                        "link": link,
                        "cover": cover,
                        "type": None,
                        "badge": badge,
                    }
                )
            return {"source": source, "data": data}
        else:
            raise await notfound(source)
    else:
        logging.error(f"Failed to retrieve data in {source}")
        raise await Failed_retrieve(source)
