from src.defs import *
while True:
    try:
        operatingSystem=checkPrefs()
        name=input('movie/series name: ')
        movies=searchSite(name)
        if not movies:
            print('no results.')
        else:
            link=pickMovie(movies)
            getDownloadLink(operatingSystem, link)
    except(KeyboardInterrupt):
        print('\n|_--> quitting...')
        break
