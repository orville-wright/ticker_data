# ticker_data

DISCLAIMER: This code is still in heavy development & design. Much of it works well, but a few areas are still early in their prototyping phase (e.g. ML & A.I). Also, the overall strategy behind the design is subject to change as code in key areas becomes more functional.
- Use at you own risk

Purpose: I built this app to Extract live stock data (raw data) from various realtime Market feeds.<br>
See the WIKI for more info: https://github.com/orville-wright/ticker_data/wiki

Currently supporting the following data sources, data extraction methods and API's...
  1. yahoo.com/finance  - BS4 web scraper/data extractor - (S/M/L/X sector/mkt-cap stats, top gainers/loosers)
  2. yahoo.com/news - BS4 web scraper/data exrtactor - all news for a ticker)
  2. alpaca.markets.com - native python API (live stock quotes, live 60 second O/H/L/C/V candlestick bars)
  3. bigcharts.marketwatch.com  - BS4 web scraper/data extarctor - (delayed stock stock & ticker details)
  4. nasdaq.com - BS4 scraper/data extractor - (delayed data)
     I leverage an old website maintained/updated by NASDAQ with live data. This webpage is easy to scrape, but the site is a slow at the market open becasue unusual volume needs to build-up significantly before being flagged as 'unusual'.
  5. marketwatch.com - BS4 web scraper/data extractor - (live quotes, ticker details)
  * The marketwatch.com module is not yet fully working.
  * marketwatch.com is a very bloated rich media site, so its slow-ish but it has nice 'realtime data' and lots of geat rich info.
  * They also enforce javascript=ON & also do highly paranoia JS testing early in the webpage setup. They are also
  * extremly paranoid about Robot scrapers & forcefully check for these early. I havent hacked arround these yet.

Data is packaged into multiple formats...
1. Pandas Data Frames
2. Numpy arrays
3. Native pythons DICT's {}
4. scikit-learn - ML Sentiment analysis of news - (ML schemes >> countvectorizer, Termdoc vocab matrix, NLTM stopwords)

This is not a backtesting framework (yawn...boring) or trade execution platform (yawn...) or a portfolio position dashboard (boring).

This tool's goal is to extract tonnes of data in real time about the market (on any day, at any moment right now) and build up a
large corpus of live data to leverage as a feed into Machine Learning, Data Science & Statistics algorithyms...in order to support
trade strategies (specifically - Day Trading & Swing Trading strategies).

There are many websites that provide considerable data and analytics in their beautifully rich web pages, but they are slow, 
over-inflated with useless bloat, riddled with targeted adds and pointless news headlines. They are unusable as a DS/ML tool for a
trader who is executing trades in real-time....but the data they show is delicious and wonderful. - Thats all you really need from
their websites.

So this tool's objective is to tak their data, poackage it into internal API methods and focus it into ONE single pool of information.
<br>
<br>

DISCLAIMER: Most websites do not like or appreciate data scraping apps/robots or apps that treat thier website as a source of raw data and extract data from thier underlying websites. Using this code might not be well-aligned with some website usage terms & conditions.

Regards,<br>
**~Orville**
