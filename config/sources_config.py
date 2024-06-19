from sources import (
    homeTeamX,
    mangaTeamX,
    chapterTeamX,
    home3asq,
    manga3asq,
    chapter3asq
)

from search import (
    searchTeamX,
    search3asq
)

# Dictionary containing source handlers
sourceHandlers = {
    "Team-X": {
        "url": "https://www.teamxnovel.com/",
        "logo": "https://www.teamxnovel.com/images/TeamX.png",
        "homePage": homeTeamX,
        "mangaPage": mangaTeamX,
        "chapterPage": chapterTeamX,
        'search': searchTeamX
    },
    "3asq": {
        "url": "https://3asq.org/manga/",
        "logo": "https://static.gameloop.com/img/34ea0309b0bbf020fa3f1be037b3baf7.png?imageMogr2/thumbnail/172.8x172.8/format/webp",
        "homePage": home3asq,
        "mangaPage": manga3asq,
        "chapterPage": chapter3asq,
        'search': search3asq
    }
}

# List of available sources for the homepage
sources = [
    {
        'url': f"/{key}",
        'img': handlers['logo'],
        'alt': f"{key} Logo",
        'name': key
    }
    for key, handlers in sourceHandlers.items()
]
