# ticker_data

**DISCLAIMER**: This code is still in heavy development & design. Much of it works well, but a few areas are still early in their prototyping phase (e.g. ML & A.I). Also, the overall strategy behind the design is subject to change as code in key areas becomes more functional.
- Use at you own risk

**SYNOPSIS**: I built this App to etract live stock data (the raw data info) from various realtime Market web feeds.<br>
See the WIKI for more info: https://github.com/orville-wright/ticker_data/wiki

The code currently supports the following data sources, data extraction methods and API's...
  1. yahoo.com/finance  - BS4 web scraper/data extractor - (S/M/L/X sector/mkt-cap stats, top gainers/loosers)
  2. yahoo.com/news - BS4 web scraper/data exrtactor - all news for a ticker)
  3. alpaca.markets.com - native python API (live stock quotes, live 60 second O/H/L/C/V candlestick bars)
  4. bigcharts.marketwatch.com  - BS4 web scraper/data extarctor - (delayed stock stock & ticker details)
  5. nasdaq.com - Native API & JSON extractor
     No BS4 scraping needed anymore (depricated)
     The old NASDAQ Unusual Volume website is ofically dead. The website is now a fancy/complex Javascript site.
     The new site is much far difficult to read as it's 100% Javascript. The new code works with native NASDAQ API & gets pure JSON data.
     The page is slow at the market open becasue unusual volume needs to build-up momentum (for 5/10 mins) before being flagged as 'unusual'.
  6. marketwatch.com - BS4 web scraper/data extractor - (live quotes, ticker details)
     * marketwatch.com module is not yet fully working.
     * marketwatch.com is a very bloated rich media site, so its slow-ish but it has nice 'realtime data' and lots of rich info.
     * They enforce javascript=ON & also do highly paranoid JS validation/checking early in the client connection setup.
     * They are paranoid about Robot scrapers & forcefully check/block these early in the setup. I havent hacked arround these yet.

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

**DISCLAIMER**: Most websites do not like or appreciate data scraping apps/robots or apps that treat thier website as a source of raw data (by extracting data from their underlying platform). Using this App might not be well-aligned with some website usage 'Terms & conditions'.  - Caveat emptor.

Regards,<br>
**~Orville**
