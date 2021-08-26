# module imports
import requests
from bs4 import BeautifulSoup
from datetime import date
import pygsheets
from os import environ #environment variables from Heroku
from sqlalchemy import create_engine
import pandas as pd

c = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')

list_var = {"AUDIO:", "IMAGE:", "VIDEO:"}
start = environ.get('STARTING_VALUE') #environment variable defining the url uid at which to start iterating

engine = create_engine(environ.get('DATABASE_URL'), echo = False)

## create or open a file to store the most recent succesfully processed uid from the url, or the starting 
try: 
  ish = c.open('initial_'+str(start))
  initial_value = ish.worksheet(property='index',value=0)
  initial = initial_value.get_value('A1', value_render='UNFORMATTED_VALUE')

except:
  c.create('initial_'+str(start))
  ish = c.open('initial_'+str(start))
  initial_value = ish.worksheet(property='index',value=0)
  initial = initial_value.update_value('A1', start)
  ish.share('fulham.davidc@gmail.com',role='writer',type='user')

## iterate through each article, and parse data 
for i in range(0, 8343244, 2):
    uid = int(initial or 13026670)+i
    headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',}

    initial = initial_value.update_value('A1', uid)
    try:
        r1 = requests.get('https://www.abc.net.au/news/'+str(uid),headers=headers,timeout=3.5,)
        
        
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
                    
                news_log = {}
                news_log["Source"] = 'ABC News'
                news_log["title"] = headline
                news_log["published_at"] = pub_date
                news_log["UID"] = uid
                news_log["published_by"] = bi_line
                news_log["body"] = body_text
                
                df = DataFrame(data=news_log)
                
                df.to_sql('news_log', con = engine, if_exists='append')
                
    except: 
      continue
