from fastapi import APIRouter, Query
from typing import Optional
from ..dependencies import get_handler, fetch_data

# إنشاء APIRouter مع إعدادات الوسوم والاستجابات المخصصة
router = APIRouter(
    tags=["Manga"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/chapter", 
    summary="Get Chapter Page", 
    response_description="Chapter page data for the specified source."
)
async def chapter(
    chapter_URL: Optional[str] = Query(
        None, 
        title="Chapter Page URL", 
        description="URL for the chapter page. Provide this URL to fetch the chapter page data."
    )
):
    """
    Retrieve the chapter page data for the specified source.

    Parameters:
    - chapter_URL (Optional[str]): The URL for the chapter page. This parameter is required to fetch the chapter page data. Defaults to None.

    Returns:
    - dict: A dictionary containing:
        - success (bool): Indicates if the operation was successful.
        - source (str): The name of the source.
        - data (dict): The data fetched from the chapter page.
    """
    # استدعاء get_handler للحصول على عنوان URL والمعالج بناءً على chapter_URL
    url, handler = await get_handler(chapter_URL)
    
    # جلب البيانات من عنوان URL باستخدام fetch_data
    result = await fetch_data(url)
    
    # معالجة البيانات المسترجعة باستخدام معالج الفصل
    results = handler["chapter_page"](result, url)

    # إرجاع قاموس يحتوي على حالة النجاح، اسم المصدر، والبيانات المسترجعة
    return {'success': True, "source": handler["name"], "data": results}
