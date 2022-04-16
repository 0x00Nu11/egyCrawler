from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
import requests, json, time, sys

useragent=UserAgent().chrome
headers={
    "accept-language": "en-US,en;q=0.9",
    "user-agent": str(useragent)
}

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
        return settings['OS']

def searchSite(query):
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

def pickMovie(movies):
    for number, title, rating, link in movies:
        print(f'ID: {number}\ntitle: {title}\nrating: {rating}\n|')
    choice=int(input('|_(choose by ID)-->> '))
    link=(movies[choice-1])[3]
    title=(movies[choice-1])[1]
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
    try:
        chosenResolution=int(input('|_(choose by number)-->> '))
        if chosenResolution<=len(attribs):
            return chosenResolution
        else:
            print('invalid option')
            chooseResolution(attribs)
    except:
        print('invalid option.')
        chooseResolution(attribs)

def chooseSeason(seasons):
    try:
        print(f'this series has {len(seasons)} seasons.\npick a season:')
        for i in range(len(seasons)):
            print(f'|Season {i+1}')
        chosenSeason=int(input(f'\n|_(choose by number)-->> '))
        if chosenSeason<=len(seasons):
            return chosenSeason
        else:
            print('invalid option')
            chooseSeason(seasons)
    except:
        print('invalid option.')
        chooseSeason(seasons)

def checkSeasons(link):
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

def chooseEpisode(episodes):
    try:
        print(f'this season has {len(episodes)} episodes.\npick an episode:')
        for i in range(len(episodes)):
            print(f'|Episode {i+1}')
        chosenEpisode=int(input(f'\n|_(choose by number)-->> '))
        if chosenEpisode<=len(episodes):
            return chosenEpisode
        else:
            print('invalid option')
            chooseEpisode(episodes)
    except:
        print('invalid option.')
        chooseEpisode(episodes)

def checkMediaType(operatingSystem, link, title):
    print('checking media type...')
    if 'series' in str(link):
        print(f'series: {title}')
        seasons=checkSeasons(link)
        chosenSeason=chooseSeason(seasons)
        chosenSeason=seasons.get(chosenSeason)
        episodes=checkEpisodes(chosenSeason)
        chosenEpisode=chooseEpisode(episodes)
        chosenEpisode=episodes.get(chosenEpisode)
        getDownloadLink(operatingSystem, chosenEpisode, title)
    else:
        print(f'movie: {title}')
        getDownloadLink(operatingSystem, link, title)

def getDownloadLink(operatingSystem, link, title):
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
    x=chooseResolution(attribs)
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
    print(f'adding {title} to downloads')
    driver.get(wgetDownload)
    
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
