# module imports
import requests
from bs4 import BeautifulSoup
from datetime import date
import pygsheets
from os import environ #environment variables from Heroku

c = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')

list_var = {"AUDIO:", "IMAGE:", "VIDEO:"}
start = 254246 #unique id from the URL from which to start scraping iterations

## Check whether a sheet with this starting unique id already exists, and if not, create one, and open it
try: 
  c.open('start_'+str(start))
except:
  c.create('start_'+str(start))
sh = c.open('start_'+str(start))
sh.share('fulham.davidc@gmail.com',role='writer',type='user')

## Set cell range and headers which will be pop
google_sheet = sh.worksheet(property='index',value=0)
google_sheet.resize(rows=100000,cols=6)
google_sheet.append_table(
    values=['Source', 'title', 'published_at', 'UID', 'published_by', 'body'])

## iterate through each article, and parse data 

for i in range(4, 8343244, 2):
    uid = start+i
    headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',}
    r1 = requests.get('https://www.abc.net.au/news/'+str(uid),allow_redirects=False,headers=headers)
    
   ## Check the web url does not return an error
 
    if r1.status_code == 200:
        coverpage = r1.content
        soup1 = BeautifulSoup(coverpage, 'html.parser')
        headline = soup1.find(
            'h1', class_='_3mBrr I7ej6 LTJIg _3qPMD _2hFDS _2Od9e _582YK _2eB4R _3Z8IO')
        date_published = soup1.find(
            'time', class_='W-g-R _14nkQ _3BwtN _2eB4R _3qdyT _3fa1F')
        bi_line = soup1.find(
            'span', class_='W-g-R _3XvRm _3BwtN _2eB4R _3qdyT _7kwJ9')
        body = soup1.find_all('p', class_='_1HzXw')
        
        ## check that headline is present and does not indicate that headline does not start with list variable
        if ((headline is not None) and (headline.get_text().startswith(tuple(list_var)) == False)):
            headline = headline.get_text()

            if date_published is not None:
                pub_date = date_published.get_text()
            else:
                pub_date = ''
            if bi_line is not None:
                author = bi_line.get_text()
            else:
                author = ''
            if body is not None:
                body_text = str(body)
            else: 
                body_text = ''
            google_sheet.append_table(values=["ABC News",headline,pub_date,uid,author,body_text])
