# egyCrawler
 spaghetti python code to download egybest content from cli
### single and batch downloads
[single download](.assets/single_download.mp4)
[batch download](.assets/batch_download.mp4)

## download
### from release
1. go to [releases](https://github.com/0x00Nu11/egyCrawler/releases) and download the respective file for your os
2. extract the compressed file anywhere
3. run the executable:
	- on linux:
		- `cd` into the extracted directory and run `./egyCrawler`
	- on windows:
		- double click the egyCrawler exe
### from source
**NOTE: make sure you have python and pip installed**
1. clone the repo or download and extract the zip
2. `cd` into the directory and run `pip install -r requirements.txt`
3. run the main script with `python main.py`

## use
1. search for a series or movie
2. - the results will be as follows:
 		- ID
 		-  name
 		-  rating
	- pick the movie/series by **ID**
3. - if it's a movie:
		1. pick a resolution
		2. when asked to start download type Y/yes to start, or n/No to keep the movie in the downloads list and add others
	- if it's a series:
		1. pick a season download method:
			- **download all:** downloads all seasons and all episodes in max resolution
			- **download range:** downloads a range of seasons between two numbers inclusive and all of their episodes in max resolution
			- **download specific:** downloads a single season or multiple specified seasons with the option to choose episode download and resolution or download all.
		2. if it's a specific season/seasons pick an episode download method:
			- **download all:** downloads all episodes in the season in max resolution
			- **download range:** downloads a range of episodes between two numbers inclusive in max resolution
			- **download specific:** downloads a single episode or multiple specified episodes with specified resolution for each
		3. when asked to start download type Y/yes to start, or n/No to keep the series in the downloads list and add others

## dependencies
**NOTE: make sure you have google chrome. you can try different chromium based browsers, though on linux you should change `browserBinary` destination on *line 187* of *defs.py* to that of your browser's binary, and download its respective chrome driver in `src`**
- google chrome
- python3
- pip
- beautifulsoup4
- fake_useragent
- plyer
- pySmartDL
- requests
- selenium
