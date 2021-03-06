from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from plyer import notification
import requests, json, time, pySmartDL, sys, os, shutil

useragent=UserAgent().chrome
headers={
    "accept-language": "en-US,en;q=0.9",
    "user-agent": str(useragent)
}

def dlProcess(lst):
    url, filename, fullName = lst[0], lst[1], lst[2]
    t0=time.time()
    try:
        notification.notify(
            title = 'egyCrawler',
            message = f'started downloading {fullName}.',
            app_icon = "src/egyCrawler-icon.ico",
            timeout = 10,
        )
        print(f'downloading "{fullName}" to "{filename}".')
        dl=pySmartDL.SmartDL(url, filename)
        dl.start()
    except Exception as e:
        return print(f'error downloading: {fullName}', e)
    with open('src/prefs.json', 'r') as prefs:
        settings=json.loads(prefs.read())
    with open('src/prefs.json', 'w') as update:
        del settings['downloads'][fullName]
        json.dump(settings, update)
    elapsed=round((time.time()-t0)/60, 3)
    notification.notify(
        title = 'egyCrawler',
        message = f'finished downloading {fullName} in {elapsed} minutes',
        app_icon = "src/egyCrawler-icon.ico",
        timeout = 10,
    )

def startDownload():
    urls=[]
    shutil.copyfile('src/prefs.json', 'src/prefscopy.json')
    with open('src/prefscopy.json', 'r') as prefscopy:
        settingscopy=json.loads(prefscopy.read())
        for fullName in settingscopy['downloads']:
            if '#' in str(fullName):
                part=str(fullName).split('#')
                name=part[0]
                season=part[1]
                if not os.path.isdir(f'downloaded/{name}'):
                    os.mkdir(f'downloaded/{name}/')
                if not os.path.isdir(f'downloaded/{name}/{season}'):
                    os.mkdir(f'downloaded/{name}/{season}')
                episode=part[2]
                url=settingscopy['downloads'].get(fullName)
                filename=f'downloaded/{name}/{season}/{episode}.mp4'
                urls.append([url, filename, fullName])
            else:
                if not os.path.isdir(f'downloaded/{fullName}'):
                    os.mkdir(f'downloaded/{fullName}')
                url=settingscopy['downloads'].get(fullName)
                filename=f'downloaded/{fullName}/{fullName}.mp4'
                urls.append([url, filename, fullName])
    os.remove('src/prefscopy.json')
    t0=time.time()
    print('donlading...\nyou will be notified when all the downloads are done.')
    for url in urls:
        dlProcess(url)
    elapsed=round((time.time()-t0)/60, 3)
    print(f'elapsed download time: {elapsed} minutes.')
    notification.notify(
        title = 'egyCrawler',
        message = f'finished all downloads in {elapsed} minutes.',
        app_icon = "src/egyCrawler-icon.ico",
        timeout = 10,
    )
    print('all done.\nyou can find your downloads in the "downloaded" directory.')

def checkPrefs():
    with open('src/prefs.json', 'r') as prefs:
        settings=json.loads(prefs.read())
        if settings['OS']=='':
            print('checking OS, this is a one time process.')
            settings['OS']=str(sys.platform)
            print(f'found OS: {sys.platform}')
            writePrefs=open('src/prefs.json', 'w+')
            writePrefs.write(json.dumps(settings))
            writePrefs.close()
        if settings['downloads']!={}:
            yN=input('the downloads list is not empty.\ndo you want to start downloading?\n|_(yes/NO)-->> ')
            if yN.lower().startswith('y'):
                startDownload()
            else:
                yN2=input('do you want to clear downloads?\n|_(yes/NO)-->> ')
                if yN2.lower().startswith('y'):
                    clearDownloads()
        return settings['OS']

def addToDownloads(name, url):
    with open('src/prefs.json', 'r') as prefs:
        settings=json.loads(prefs.read())
        settings['downloads'][str(name)]=url
        print(f'added {name} to downloads')
        writePrefs=open('src/prefs.json', 'w+')
        writePrefs.write(json.dumps(settings))
        writePrefs.close()
    notification.notify(
        title = 'egyCrawler',
        message = f'added {name} to download list.',
        app_icon = "src/egyCrawler-icon.ico",
        timeout = 10,
    )

def clearDownloads():
    with open('src/prefs.json', 'r') as prefs:
        settings=json.loads(prefs.read())
        settings['downloads']={}
        writePrefs=open('src/prefs.json', 'w+')
        writePrefs.write(json.dumps(settings))
        writePrefs.close()
        print('cleared downloads.')
    notification.notify(
        title = 'egyCrawler',
        message = f'cleared download list.',
        app_icon = "src/egyCrawler-icon.ico",
        timeout = 10,
    )

def searchSite(query):
    global headers
    print(f'searching for "{query}", this might take a few seconds depending on your internet speed.')
    moviesList=[]
    query=f"https://lake.egybest.life/explore/?q={makeURL(query)}"
    text=requests.get(query, headers=headers).text
    soup=BeautifulSoup(text, 'html.parser')
    mainFrame=soup.find_all('div', class_='movies')
    for i in mainFrame:
        movie=i.find_all('a')
        for j in movie:
            try:
                number=movie.index(j)+1
                link=j['href']
                title=j.find(class_='title').text
                rating=j.find(class_='i-fav rating').text
                moviesList.append([(number), (title), (rating), (link)])
            except:
                pass
    return moviesList

def makeURL(query):
    return "".join([i.replace(' ', '-') for i in str(query).lower() if i.isalpha() or i.isdigit() or i==' ']).rstrip()

def makeName(title):
    return "".join([str(i).replace('season-', 'S').replace('ep-', 'E').replace('-', ' ') for i in str(title)])

def pickMovie(movies):
    for number, title, rating, link in movies:
        print(f'ID: {number}\ntitle: {title}\nrating: {rating}\n|')
    choice=input('|_(choose by ID)-->> ')
    if choice.isdigit() and 0<int(choice)<len(movies):
        link=(movies[int(choice)-1])[3]
        title=(movies[int(choice)-1])[1]
        return link, makeURL(str(title))
    else:
        print(f'invalid option. defaulting to the first entry: "{movies[0][1]}"')
        link=(movies[0])[3]
        title=(movies[0])[1]
        return link, makeURL(str(title))

def setupSelenium(operatingSystem):
    chromeOptions=webdriver.ChromeOptions()
    chromePrefs={}
    chromePrefs["profile.managed_default_content_settings.images"] = 2
    chromePrefs["profile.default_content_settings.images"] = 2
    chromeOptions.add_experimental_option("prefs", chromePrefs)
    chromeOptions.add_argument('--incognito')
    chromeOptions.add_argument('--log-level=OFF')
    chromeOptions.add_argument('--disable-extensions')
    chromeOptions.add_argument('--headless')
    chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
    if operatingSystem=='linux':
        driverBinary=f'src/chromedriver'
        browserBinary=f'/usr/bin/google-chrome-stable'
        chromeOptions.binary_location=browserBinary
    else:
        driverBinary=f'src/chromedriver.exe'
    driver=webdriver.Chrome(executable_path=driverBinary, chrome_options=chromeOptions)
    return driver

def chooseResolution(attribs):
    count=1
    for quality, resolution, size, button in attribs:
        print(f'{count}- quality: {str(quality).strip()}, resolution: {str(resolution).strip()}, size: {str(size).strip()}')
        count+=1
    chosenResolution=input('|_(choose by number)-->> ')
    if chosenResolution.isdigit() and int(chosenResolution)<=len(attribs):
        return int(chosenResolution)
    else:
        print(f'invalid option. defaulting to the highest resolution: {(attribs[1][0])}')
        return 1

def chooseSeason(seasons):
    print(f'this series has {len(seasons)} seasons. do you want to:')
    print('1- download all\n2- download range (e.g: 5 - 13)\n3- download specific seasons (e.g: 1, 7, 6, 8)')
    try:
        chosenPattern=int(input(f'\n|_(choose by number)-->> '))
        chosenPattern=(chosenPattern if 0<chosenPattern<=3 else 3)
    except:
        print('invalid option. defaulting to option 3: specific seasons.')
        chosenPattern=3
    if chosenPattern==1:
        print(f'downloading all {len(seasons)} seasons.')
        seasonslist=[]
        for i in range(len(seasons)):
            seasonslist.append(i+1)
        return seasonslist, 'auto'
    elif chosenPattern==2:
        try:
            print('choose range of seasons (n - m):')
            seRange=list(map(int, input('|_(n - m)--> ').replace(' ', '').split('-')))
            seRange=[abs(i) for i in seRange]
            seRange=[j+1 if j==0 else (len(seasons) if j>len(seasons) else j) for j in seRange]
            print(f'downloading from season {seRange[0]} to season {seRange[1]}')
            seasonslist=[]
            for k in range(seRange[0], seRange[1]+1):
                seasonslist.append(k)
            return seasonslist, 'auto'
        except:
            print(f'invalid range. defaulting to latest season: season {len(seasons)}')
            return list(len(seasons)), 'man'
    else:
        for i in range(len(seasons)):
            print(f'season {i+1}')
        try:
            sesList=list(map(int, input('|_(x, y, z)-->> ').replace(' ', '').split(',')))
            sesList=[abs(j) for j in sesList]
            sesList=[k+1 if k==0 else (len(seasons) if k>len(seasons) else k) for k in sesList]
            print('downloading seasons: '+', '.join([str(l) for l in sesList]))
            seasonslist=[]
            for m in sesList:
                seasonslist.append(m)
            return seasonslist, 'man'
        except:
            print(f'invalid option. defaulting to the latest season: season {len(seasons)}')
            return [len(seasons)], 'man'


def checkSeasons(link):
    global headers
    seasons={}
    text=requests.get(link, headers=headers).text
    soup=BeautifulSoup(text, 'html.parser')
    box=soup.find('div', class_='contents movies_small')
    elements=box.find_all('a')
    count=len(elements)
    for element in elements:
        url=element['href']
        season={count:str(url)}
        seasons.update(season)
        count-=1
    return seasons

def checkEpisodes(chosenSeason):
    global headers
    episodes={}
    text=requests.get(chosenSeason, headers=headers).text
    soup=BeautifulSoup(text, 'html.parser')
    box=soup.find('div', class_='movies_small')
    elements=box.find_all('a')
    count=len(elements)
    for element in elements:
        url=element['href']
        episode={count:str(url)}
        episodes.update(episode)
        count-=1
    return episodes

def choosePattern(episodes):
    print(f'this season has {len(episodes)} episodes.\ndo you want to:')
    print(f'1- download all\n2- download range (e.g: 5 - 13)\n3- download specific episodes (e.g: 1, 7, 6, 8)')
    try:
        chosenPattern=int(input(f'\n|_(choose by number)-->> '))
        return chosenPattern if 0<chosenPattern<=3 else 3
    except:
        print('invalid option. defaulting to option 3: specific episodes.')
        return 3

def chooseEpisodes(operatingSystem, chosenPattern, chosenSeason, episodes, title, mode='man'):
    if chosenPattern==1:
        print('downloading all episodes')
        for i in range(len(episodes)):
            getDownloadLink(operatingSystem, episodes.get(i+1), title, single=False, season=chosenSeason, episode=i+1)
    elif chosenPattern==2:
        try:
            print('choose range of episodes (n - m):')
            epRange=list(map(int, input('|_(n - m)--> ').replace(' ', '').split('-')))
            epRange=[abs(i) for i in epRange]
            epRange=[j+1 if j==0 else (len(episodes) if j>len(episodes) else j) for j in epRange]
            print(f'downloading from episode {epRange[0]} to episode {epRange[1]}')
            for k in range(epRange[0], epRange[1]+1):
                getDownloadLink(operatingSystem, episodes.get(k), title, single=False, season=chosenSeason, episode=k)
        except:
            print(f'invalid range. defaulting to latest two episodes: episode {len(episodes)-1} and episode {len(episodes)}')
            for k in range(len(episodes)-1, len(episodes)+1):
                getDownloadLink(operatingSystem, episodes.get(k), title, single=False, season=chosenSeason, episode=k)
    else:
        for i in range(len(episodes)):
            print(f'episode {i+1}')
        try:
            epsList=list(map(int, input('|_(x, y, z)-->> ').replace(' ', '').split(',')))
            epsList=[abs(j) for j in epsList]
            epsList=[k+1 if k==0 else (len(episodes) if k>len(episodes) else k) for k in epsList]
            print('downloading episodes: '+', '.join([str(l) for l in epsList]))
            for m in epsList:
                getDownloadLink(operatingSystem, episodes.get(int(m)), title, season=chosenSeason, episode=m, defaultName=False)
        except:
            print(f'invalid option. defaulting to the latest episode: episode {len(episodes)}')
            getDownloadLink(operatingSystem, episodes.get(len(episodes)), title, season=chosenSeason, episode=len(episodes), defaultName=False)
    if mode!='auto':
        yN=input('start download?\n|_("y/Y/yes" to start, "n/N/no" to continue)-->> ')
        if yN.lower().startswith('y'):
            startDownload()
                

def checkMediaType(operatingSystem, link, title):
    print('checking media type...')
    if 'series' in str(link):
        print(f'series: {makeName(title)}')
        seasons=checkSeasons(link)
        chosenSeason, mode=chooseSeason(seasons)
        for i in chosenSeason:
            chosenSeasonLink=seasons.get(i)
            episodes=checkEpisodes(chosenSeasonLink)
            if mode=='auto':
                chosenPattern=1
                chooseEpisodes(operatingSystem, chosenPattern, i, episodes, title, mode)
                startDownload()
            else:
                chosenPattern=choosePattern(episodes)
                chooseEpisodes(operatingSystem, chosenPattern, i, episodes, title)
    elif 'anime' in str(link):
        print(f'anime: {makeName(title)}')
        seasons=checkSeasons(link)
        chosenSeason, mode=chooseSeason(seasons)
        for i in chosenSeason:
            chosenSeasonLink=seasons.get(i)
            eps=checkEpisodes(chosenSeasonLink)
            nums=[]
            lnks=[]
            episodes={}
            for elem in eps:
                nums.append(elem)
                lnks.append(eps.get(elem))
            nums.reverse()
            episodes={nums[i]: lnks[i] for i in range(len(nums))}
            if mode=='auto':
                chosenPattern=1
                chooseEpisodes(operatingSystem, chosenPattern, i, episodes, title, mode)
                startDownload()
            else:
                chosenPattern=choosePattern(episodes)
                chooseEpisodes(operatingSystem, chosenPattern, i, episodes, title)
    else:
        print(f'movie: {makeName(title)}')
        getDownloadLink(operatingSystem, link, title)

def getDownloadLink(operatingSystem, link, title, single=True, defaultName=True, season='', episode=''):
    global headers
    print('getting available resolutions, this will take a while depending on your internet speed.')
    driver=setupSelenium(operatingSystem)
    text=requests.get(link, headers=headers).text
    driver.get(link)
    time.sleep(3)
    driver.execute_script('window.stop();')
    soup=BeautifulSoup(text, 'html.parser')
    infoTable=soup.find('tbody')
    infoHeaders=infoTable.find_all('tr')
    td=[tr.find_all('td') for tr in infoHeaders]
    attribs=[]
    for i in td:
        quality=i[0].text
        resolution=i[1].text
        size=i[2].text
        dl=i[3]
        buttons=dl.find('a')
        attribs.append([quality, resolution, size, buttons])
    if single:
        x=chooseResolution(attribs)
    else:
        x=1
    downloadURL=''
    wgetDownload=''
    while downloadURL=='':
        driver.set_page_load_timeout(3)
        try:
            time.sleep(1)
            currentURL=driver.current_url
            if 'egybest' in str(currentURL):
                downloadURL=manageRedirects(driver, currentURL, x, title)
            else:
                print('closing ads...')
                driver.close()
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            time.sleep(1)
        except(TimeoutException):
            driver.execute_script('window.stop();')
            continue
    while wgetDownload=='':
        driver.set_page_load_timeout(5)
        try:
            time.sleep(1)
            currentURL=driver.current_url
            if 'egybest' in str(currentURL):
                wgetDownload=fetchDownload(driver, downloadURL, currentURL)
            else:
                print('closing ads...')
                driver.close()
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            time.sleep(1)
        except(TimeoutException):
            driver.execute_script('window.stop();')
            continue
    if not single or not defaultName:
        title=makeName(title)
        title=f'{title}#season {season}#episode {episode}'
        addToDownloads(title, wgetDownload)
    else:
        print(f'adding {makeName(title)} to downloads')
        addToDownloads(makeName(title), wgetDownload)
    driver.quit()
    if single and defaultName:
        yN=input('start download?\n|_("y/Y/yes" to start, "n/N/no" to continue)-->> ')
        if yN.lower().startswith('y'):
            startDownload()

def manageRedirects(driver, currentURL, x, title):
    if '&r=' in str(currentURL):
        print("request was blocked. make sure you don't have adblock.\nretrying...")
        reloadPage=driver.find_element_by_xpath('//*[@id="mainLoad"]/div/a')
        ActionChains(driver).click(reloadPage).perform()
    elif '?refresh=' in str(currentURL):
        driver.close()
    elif 'vs-mirror' in str(currentURL):
        print('fetching download URL...')
        downloadURL=str(currentURL)
        return downloadURL
    else:
        if str(title) in str(currentURL):
            print('fetching download page...')
            button=driver.find_element_by_xpath(f'//*[@id="watch_dl"]/table/tbody/tr[{x}]/td[4]/a[1]')
            ActionChains(driver).click(button).perform()
        else:
            print('closing ads...')
            driver.close()
    return ''

def fetchDownload(driver, downloadURL, currentURL):
    if str(downloadURL) not in str(currentURL):
        print('closing ads and unnecessary tabs...')
        driver.close()
    else:
        dlButton=driver.find_element_by_xpath('/html/body/div[1]/div/p/a[1]')
        dlbClass=dlButton.get_attribute('class')
        if dlbClass=='bigbutton':
            wgetDownload=dlButton.get_attribute('href')
            print('found the download URL.')
            return wgetDownload
        else:
            ActionChains(driver).click(dlButton).perform()
    return ''
