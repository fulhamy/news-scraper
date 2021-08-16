import requests
from bs4 import BeautifulSoup
import csv
from datetime import date
import re
import pygsheets

success_counter = 0
today = date.today()
list_var = {"AUDIO:", "IMAGE:", "VIDEO:"}
start = 254246

cred_file = GDRIVE_API_CREDENTIALS
c = pygsheets.authorize(service_file=cred_file)
sh = c.create('start_'+str(start))
nwks = sh.add_worksheet("data", rows=100000, cols=5)
nwks.append_table(
    values=['Source', 'title', 'published_at', 'UID', 'published_by', 'body'])
google_sheet = c.open('start_'+str(start))
wks = google_sheet.worksheet_by_title('data')
success_counter = 0
for i in range(4, 22, 2):
    uid = start+i
    r1 = requests.get('https://www.abc.net.au/news/'+str(uid))
    if r1.status_code == 200:
        coverpage = r1.content
        soup1 = BeautifulSoup(coverpage, 'html.parser')
        coverpage_news = soup1.find(
            'h1', class_='_3mBrr I7ej6 LTJIg _3qPMD _2hFDS _2Od9e _582YK _2eB4R _3Z8IO')
        date_published = soup1.find(
            'time', class_='W-g-R _14nkQ _3BwtN _2eB4R _3qdyT _3fa1F')
        bi_line = soup1.find(
            'span', class_='W-g-R _3XvRm _3BwtN _2eB4R _3qdyT _7kwJ9')
        body = soup1.find_all('p', class_='_1HzXw')
        if ((coverpage_news is not None) and (coverpage_news.get_text().startswith(tuple(list_var)) == False)):
            headline = coverpage_news.get_text()

            if date_published is not None:
                pub_date = date_published.get_text()
            else:
                pub_date = ''
            if bi_line is not None:
                author = bi_line
            else:
                author = ''
            if body is not None:
                body_text = body
            else: 
                body_text = ''
            wks2 = google_sheet.worksheet_by_title('data')
            wks2.append_table(values=["ABC News3",headline,pub_date,uid,author,body_text])
