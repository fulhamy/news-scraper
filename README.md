# ABC News Scraper

This script searches for the below data fields in the Australian Broadcasting Corporation's online news site, ABC News Online: https://www.abc.net.au/news/. 

1. Byline
2. Published Date
3. Headline
4. Article Body

Then, a running count is stored in a google sheet to maintain position in the event of outages or downtime.  

After handling errors, successful scrapes are stored in a Heroku database for later analysis. 
