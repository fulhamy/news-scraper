import requests
from bs4 import BeautifulSoup
from datetime import date
import pygsheets
from os import environ  # environment variables from Heroku
from sqlalchemy import create_engine
from pandas import DataFrame

c = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')

list_var = {"AUDIO:", "IMAGE:", "VIDEO:"}
start = environ.get('STARTING_VALUE')  # environment variable defining the url uid at which to start iterating

engine = create_engine(environ.get('DATABASE_URL'), echo=False)

# create or open a file to store the most recent succesfully processed uid from the url, or the starting
try:
    ish = c.open('initial_' + str(start))
    wks = ish.worksheet_by_title('Sheet1')
    initial = wks.get_value('A1', value_render='UNFORMATTED_VALUE')

except:
    c.create('initial_' + str(start))
    ish = c.open('initial_' + str(start))
    wks = ish.worksheet_by_title('Sheet1')
    wks.update_value('A1', start)
    ish.share('fulham.davidc@gmail.com', role='writer', type='user')
    initial = wks.get_value('A1', value_render='UNFORMATTED_VALUE')

# iterate through each article, and parse data
for i in range(0, 8343244, 2):
    
    uid = initial + i
    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.131 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=10',
        'Connection': 'keep-alive', }

    print("UID created by iteration=" + str(uid))
    
    initial = wks.update_value('A1', uid)
    
    print("Check UID from spreadsheet=" + str(wks.get_value('A1', value_render='UNFORMATTED_VALUE')))
    
    try:
        r1 = requests.get('https://www.abc.net.au/news/' + str(uid), headers=headers, timeout=None)
        print("UID=" + str(uid) + " status=" + str(r1.status_code))

        # Check the web url does not return an error

        if r1.status_code == 200:
            coverpage = r1.content
            soup1 = BeautifulSoup(coverpage, 'html.parser')
            # headline = soup1.find('h1', class_='_24eQK _3O3fw _23WqP _2yZBa UOKdn _3I3Xh _2uBSR _10YQT _1lh6E')
            headline = soup1.find('h1')
            # date_published = soup1.find('time', class_='_3rsys _1srG4 _3PhF6 _10YQT _2Cu8q _1yU-k')
            date_published = soup1.find('time')
            bi_line = soup1.find(class_='_3rsys _1cBaI _3PhF6 _10YQT _2Cu8q _7kwJ9')
            body = soup1.find_all('p', class_='_1HzXw')
            

            # check that headline is present and does not indicate that headline does not start with list variable
            # here I just printed every var to see their value
            if (headline is not None) and (headline.get_text().startswith(tuple(list_var)) is False):
                headline = headline.get_text()

                if date_published is not None:
                    pub_date = date_published.get_text()
                else:
                    pub_date = None
                if bi_line is not None:
                    author = bi_line.get_text()
                else:
                    author = None
                if body is not None:
                    body_text = str(body)
                else:
                    body_text = None

                news_log = {"Source": 'ABC News', "title": headline, "published_at": pub_date, "UID": uid,
                            "published_by": author, "body": body_text}

                df = DataFrame(data=news_log, index=[0])

                df.to_sql('news_log', con=engine, if_exists='append')
            else:
                print("Exit with no headline, UID=" +str(uid))
                continue
        else:
            print("Exit with error="+ str(r1.status_code))
            continue
    except:
        print("Exit with no request, UID=" +str(uid))
        continue
