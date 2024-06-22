# import os
# import pkgutil
# import importlib

# package_dir = os.path.dirname(__file__)

# for (_, module_name, _) in pkgutil.iter_modules([package_dir]):
#     module = importlib.import_module(f".{module_name}", package=__name__)
#     for attribute_name in dir(module):
#         if not attribute_name.startswith("_"):
#             globals()[attribute_name] = getattr(module, attribute_name)


from .PyProbe import pyparse

from .search import search_teamx, search3asq

from .sources import ( 
    home_teamx,
    manga_teamx,
    chapter_teamx,
    home3asq,
    manga3asq,
    chapter3asq
)


__all__ = [ 
    "pyparse",
    "search_teamx", 
    "search3asq", 
    'home_teamx', 
    'manga_teamx', 
    'chapter_teamx', 
    'home3asq', 
    'manga3asq', 
    'chapter3asq'
]