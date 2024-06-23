from scraper import (
    home_teamx,
    manga_teamx,
    chapter_teamx,
    home3asq,
    manga3asq,
    chapter3asq
)

from scraper import (
    search_teamx,
    search3asq
)

from typing import List, Dict
from typing import Optional, Union, Dict, Any


# Dictionary containing source handlers
source_handlers = [
    {
        "name": "Team-X",
        "base_url": "https://www.teamxnovel.com/",
        "logo_url": "https://www.teamxnovel.com/images/TeamX.png",
        "home_page": home_teamx,
        "manga_page": manga_teamx,
        "chapter_page": chapter_teamx,
    },
    {
        "name": "3asq",
        "base_url": "https://3asq.org/manga/",
        "logo_url": "https://static.gameloop.com/img/34ea0309b0bbf020fa3f1be037b3baf7.png?imageMogr2/thumbnail/172.8x172.8/format/webp",
        "home_page": home3asq,
        "manga_page": manga3asq,
        "chapter_page": chapter3asq
    }
]

# Define searchHandlers dictionary

"""
Extract useful information for API users from source handlers.
"""
get_sources = [
    {
        'name': handler['name'],
        'query_param': handler['name'],
        'base_url': handler.get('base_url'),
        'logo_url': handler.get('logo_url'),
    }
    for handler in source_handlers
]

search_handlers = [
    {
        "name": "Team-X",
        "search_URL": "https://www.teamxnovel.com/ajax/search",
        "method": "GET",
        "search": search_teamx,
        "headers": {
            'authority': 'www.teamxnovel.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json;charset=UTF-8'
        },
        "params": lambda keyword: {'keyword': keyword},
    },
    {
        "name": "3asq",
        "search_URL": "https://3asq.org/wp-admin/admin-ajax.php",
        "search": search3asq,
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": "\"Android\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        },
        "data": lambda keyword: {"action": "wp-manga-search-manga", "title": keyword},
    }
]