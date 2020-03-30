# ticker_data
Extract live stock data from vasrious realtime Market feeds.

Currently supporting the following data sources, data extraction methods and API's...
  1. yahoo.com/finance  - BS4 web scraper/data extractor - (S/M/L/X sector/mkt-cap stats, top gainers/loosers)
  2. yahoo.com/news - BS4 web scraper/data exrtactor - all news for a ticker)
  2. alpaca.markets.com - native python API (live stock quotes, live 60 second O/H/L/C/V candlestick bars)
  3. bigcharts.marketwatch.com  - BS4 web scraper/data extarctor - (delayed stock stock & ticker details)
  4. marketwatch.com - BS4 web scraper/data extractor - (live quotes, ticker details)
  * The marketwatch.com module is not yet fully working.
  * marketwatch.com is vert bloated rich media site, so its slow-ish but it has realtime quotes and lots of geat data.
  * They also enforce javascript=ON & also do highly paranoia JS testing early in the webpage setup. They are also
  * extremly paranoid about Robot scrapers & forcefully check for these early. I havent hacked arround these yet.

Data is packaged into multipel formats...
1. Pandas Data Frames
2. Numpy arrays
3. Native pythons DICT's {}
4. scikit-learn - ML Sentiment analysis of news - (ML schemes >> countvectorizer, Termdoc vocab matrix, NLTM stopwords)

This is not a backtesting framework (yawn...boring) or trade execution platform (yawn...) or a portfolio position dashboard (boring).

This tool's goal is to extract tonnes of data in real time about the market (on any day, at any moment right now) and build up a
large corpus of live data to leverage as a feed into Machine Learning, Data Science & Statistics algorithyms...in order to support
trade strategies (specifically - multiple Day Trading & Swing Trading strategies).

There are many websites that provide considerable data and analytics in their beautifully rich web pages, but they are slow, 
over-inflated with useless bloat, riddled with targeted adds and pointless news headlines. They are unusable as a DS/ML tool for a
trader who is executing real trades in real-time....but the data they show is delicious and wonderful. - Thats all you really need from
their websites.

So this tool is focused taking their data and focusing it into ONE single pool of information.


~Orville
