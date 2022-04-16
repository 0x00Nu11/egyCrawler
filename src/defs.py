from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains
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
    soup=BeautifulSoup(text, 'lxml')
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
    return "".join([i for i in query if i.isalpha() or i.isdigit() or i==' ']).rstrip()

def pickMovie(movies):
    for number, title, rating, link in movies:
        print(f'ID: {number}\ntitle: {title}\nrating: {rating}\n|')
    choice=int(input('|_(choose by ID)-->> '))
    link=(movies[choice-1])[3]
    return link

def setupSelenium(operatingSystem):
    chromeOptions=webdriver.ChromeOptions()
    chromePrefs={}
    chromePrefs["download.download_restrictions"]=0
    chromeOptions.add_experimental_option("prefs", chromePrefs)
    chromeOptions.add_argument('--incognito')
    #chromeOptions.add_argument('--headless')
    #chromeOptions.add_argument('--log-level=OFF')
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
        print(f'{count}- {resolution}, size: {size}')
        count+=1
    try:
        chosenResolution=int(input('|_(choose by number)-->> '))
        return chosenResolution
    except:
        print('invalid option.')
        chooseResolution(attribs)

def getDownloadLink(operatingSystem, link):
    print('getting available resolutions, this will take a while depending on your internet speed.')
    driver=setupSelenium(operatingSystem)
    text=requests.get(link, headers=headers).text
    driver.get(link)
    soup=BeautifulSoup(text, 'lxml')
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
    refresh='?refresh='
    redirect='&r='
    vsmirror='vs-mirror'
    downloadURL=''
    while downloadURL=='':
        time.sleep(1)
        driver.execute_script("window.stop();")
        if 'egybest' not in str(driver.current_url):
            print('closing popup ads and redirects.')
            driver.close()
        elif vsmirror in str(driver.current_url):
            print('fetching download URL.')
            downloadURL=str(driver.current_url)
            break
        elif refresh in str(driver.current_url):
            driver.close()
        elif redirect in str(driver.current_url):
            print("request was blocked. make sure you don't have adblock.\nretrying...")
            reloadPage=driver.find_element_by_xpath('//*[@id="mainLoad"]/div/a')
            ActionChains(driver).click(reloadPage).perform()
        else:
            print('fetching download page')
            button=driver.find_element_by_xpath(f'//*[@id="watch_dl"]/table/tbody/tr[{x}]/td[4]/a[1]')
            ActionChains(driver).click(button).perform()
        driver.switch_to_window(driver.window_handles[len(driver.window_handles)-1])

    wgetLink=''
    while True:
        currentURL=driver.current_url
        driver.execute_script("window.stop();")
        if str(currentURL)!=str(downloadURL) and 'ebybest' not in str(currentURL):
            driver.close()
            driver.switch_to_window(driver.window_handles[len(driver.window_handles)-1])
        elif str(currentURL)!=str(downloadURL) and 'egybest' in str(currentURL):
            print('retrying to fetch download page')
            button=driver.find_element_by_xpath(f'//*[@id="watch_dl"]/table/tbody/tr[{x}]/td[4]/a[1]')
            ActionChains(driver).click(button).perform()
        else:
            downloadButton=driver.find_element_by_xpath('/html/body/div[1]/div/p/a[1]')
            wgetLink=downloadButton.get_attribute('href')
            if wgetLink=='' or wgetLink==None:
                ActionChains(driver).click(downloadButton).perform()
            else:
                break
    print(wgetLink)
    
def manageRedirects():
    while downloadURL=='':
        time.sleep(1)
        driver.execute_script("window.stop();")
        if 'egybest' not in str(driver.current_url):
            print('closing popup ads and redirects.')
            driver.close()
        elif vsmirror in str(driver.current_url):
            print('fetching download URL.')
            downloadURL=str(driver.current_url)
            break
        elif refresh in str(driver.current_url):
            driver.close()
        elif redirect in str(driver.current_url):
            print("request was blocked. make sure you don't have adblock.\nretrying...")
            reloadPage=driver.find_element_by_xpath('//*[@id="mainLoad"]/div/a')
            ActionChains(driver).click(reloadPage).perform()
        else:
            print('fetching download page')
            button=driver.find_element_by_xpath(f'//*[@id="watch_dl"]/table/tbody/tr[{x}]/td[4]/a[1]')
            ActionChains(driver).click(button).perform()
        driver.switch_to_window(driver.window_handles[len(driver.window_handles)-1])
    wgetLink=''
    while True:
        currentURL=driver.current_url
        driver.execute_script("window.stop();")
        if str(currentURL)!=str(downloadURL) and 'ebybest' not in str(currentURL):
            driver.close()
            driver.switch_to_window(driver.window_handles[len(driver.window_handles)-1])
        elif str(currentURL)!=str(downloadURL) and 'egybest' in str(currentURL):
            print('retrying to fetch download page')
            button=driver.find_element_by_xpath(f'//*[@id="watch_dl"]/table/tbody/tr[{x}]/td[4]/a[1]')
            ActionChains(driver).click(button).perform()
        else:
            downloadButton=driver.find_element_by_xpath('/html/body/div[1]/div/p/a[1]')
            wgetLink=downloadButton.get_attribute('href')
            if wgetLink=='' or wgetLink==None:
                ActionChains(driver).click(downloadButton).perform()
            else:
                break
    print(wgetLink)
    
def fetchDownload():
    while downloadURL=='':
        try:
            time.sleep(1)
            driver.execute_script("window.stop();")
            if 'egybest' not in str(driver.current_url):
                print('closing popup ads and redirects.')
                driver.close()
            elif vsmirror in str(driver.current_url):
                print('fetching download URL.')
                downloadURL=str(driver.current_url)
                break
            elif refresh in str(driver.current_url):
                driver.close()
            elif redirect in str(driver.current_url):
                print("request was blocked. make sure you don't have adblock.\nretrying...")
                reloadPage=driver.find_element_by_xpath('//*[@id="mainLoad"]/div/a')
                ActionChains(driver).click(reloadPage).perform()
            else:
                print('fetching download page')
                button=driver.find_element_by_xpath(f'//*[@id="watch_dl"]/table/tbody/tr[{x}]/td[4]/a[1]')
                ActionChains(driver).click(button).perform()
            driver.switch_to_window(driver.window_handles[len(driver.window_handles)-1])
        except:
            pass
    wgetLink=''
    while True:
        currentURL=driver.current_url
        driver.execute_script("window.stop();")
        if str(currentURL)!=str(downloadURL) and 'ebybest' not in str(currentURL):
            driver.close()
            driver.switch_to_window(driver.window_handles[len(driver.window_handles)-1])
        elif str(currentURL)!=str(downloadURL) and 'egybest' in str(currentURL):
            print('retrying to fetch download page')
            button=driver.find_element_by_xpath(f'//*[@id="watch_dl"]/table/tbody/tr[{x}]/td[4]/a[1]')
            ActionChains(driver).click(button).perform()
        else:
            downloadButton=driver.find_element_by_xpath('/html/body/div[1]/div/p/a[1]')
            wgetLink=downloadButton.get_attribute('href')
            if wgetLink=='' or wgetLink==None:
                ActionChains(driver).click(downloadButton).perform()
            else:
                break
    print(wgetLink)