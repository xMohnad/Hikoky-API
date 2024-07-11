# Dictionary containing source handlers
source_handlers = [
    {
        "name": "Team-X",
        "base_url": "https://www.teamxnovel.com/",
        "logo_url": "https://www.teamxnovel.com/images/TeamX.png",
    },
    {
        "name": "3asq",
        "base_url": "https://3asq.org/manga/",
        "logo_url": "https://static.gameloop.com/img/34ea0309b0bbf020fa3f1be037b3baf7.png?imageMogr2/thumbnail/172.8x172.8/format/webp",
    },
]

get_sources = [
    {
        "name": handler["name"],
        "query_param": handler["name"],
        "base_url": handler.get("base_url"),
        "logo_url": handler.get("logo_url"),
    }
    for handler in source_handlers
]
