from .search import Search

from .manga import (
    # Home page for displaying manga for the source
    Home, 
    MangaDetails,
    LatestChapters,
    
    # Manga display page for the source
    Manga,
    MangaInfo, 
    ChapterDetails,
    
    # Chapter presentation page
    Chapter, 
    
    BaseModel
)


# Unified class inheriting from all data classes and Search
class MangaFusion(Search, LatestChapters, MangaDetails, Home, MangaInfo, ChapterDetails, Manga, Chapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



__all__ = [
    "Search",
    'BaseModel',
    'LatestChapters', 
    'MangaDetails', 
    'Home', 
    'MangaInfo', 
    'ChapterDetails', 
    'Manga', 
    'Chapter',
    'MangaFusion'
]



"""
# Example of saving data using MangaFusion
data_list = [
    MangaFusion(name='Naruto', link='www.teamxnovel.com/Naruto', source='teamx'),
    MangaFusion(name='Attack on Titan', link='www.teamxnovel.com/Attack-on-Titan', source='teamx'),
    MangaFusion(name='Naruto', link='3asq.org/Naruto', source='3asq'),
    MangaFusion(name='Attack on Titan', link='3asq.org/Attack-on-Titan', source='3asq')
]

for data in data_list:
    data.save()

# Example of searching data by source using MangaFusion
results_by_source = MangaFusion.search_by_source('teamx', 'Naruto')

# Print results
print("Results by Source:")
for result in results_by_source:
    print(result)
"""
