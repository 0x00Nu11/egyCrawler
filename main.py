from src.defs import *
display = Display(visible=0, size=(800, 600))
display.start()

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
display.stop()