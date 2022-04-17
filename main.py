from src.defs import *

operatingSystem=checkPrefs()
while True:
    try:
        name=input('movie/series name: ')
        movies=searchSite(name)
        if not movies:
            print('no results.')
        else:
            link, title=pickMovie(movies)
            checkMediaType(operatingSystem, link, title)
    except(KeyboardInterrupt):
        print('\n|_--> quitting...')
        break