# ticker_data

Date: 29 August 2021
** Major updates **
- Lots of things were broken over the past 6 months. They are now all fixed.
- JavaScript page data processing/scraping is now fully working.
- Nasadaq.com has been added as a reliable data source (pure JSON API access & JavaScript scraping)


**DISCLAIMER**: This code is still in heavy development & design. Much of it works well, but a few areas are still early in their prototyping phase (e.g. ML & A.I). Also, the overall strategy behind the design is subject to change as code in key areas becomes more functional.
- Use at you own risk

**SYNOPSIS**: I built this App to extract live stock data (the raw data info) from various real-time Market web feeds.<br>
It's main role is to literally *get at the raw data*, so you can do much more interesting things with it.<br>
See the WIKI for more info: https://github.com/orville-wright/ticker_data/wiki

The code currently supports the following data sources, data extraction methods and API's...
  1. yahoo.com/finance  - BS4 web scraper/data extractor - (S/M/L/X sector/mkt-cap stats, top gainers/looser)
  2. yahoo.com/news - BS4 web scraper/data extractor - all news for a ticker)
  3. alpaca.markets.com - native python API (live stock quotes, live 60 second O/H/L/C/V candlestick bars)
  4. bigcharts.marketwatch.com
      * live quotes (15 m ins delayed)
      * live company ticker details
      * All data comes via BS4 web scraper/data extractor
  5. nasdaq.com - Native API & JSON extractor
     * live real-time quotes
     * No more BS4 scraping needed (deprecated)
     * The old NASDAQ Unusual Volume website is officially dead. The website is now a fancy/complex JavaScript site.
     * The new site is more difficult to read as it's 100% JavaScript. The new code works with native NASDAQ API & gets pure JSON data.
     * WARN: page is slow at the market open because unusual volume needs to build-up momentum (for 5/10 mins) before being flagged as 'unusual'.
  6. marketwatch.com
     * live news feed processor/reader to assist ML and AI intelligence code
     * marketwatch.com new scraper module is not yet fully working. Although JavaScript scraping is now working in general.
     * marketwatch.com is a very bloated rich media site, so its slow-ish but it has nice 'real-time data' and lots of rich info for ML & AI.
     * Site is paranoid about JS validation/checking early in the client connection setup, so needs JS hack treatment.

Once I've extracted the Data, I package into a few formats...
1. Pandas Data Frames
2. Numpy arrays
3. Native pythons DICT's {}
4. scikit-learn - ML Sentiment analysis of news - (ML schemes >> countvectorizer, Termdoc vocab matrix, NLTM stopwords)

This is not a Backtesting framework (yawn...boring) or Day Trading trade execution platform (yawn...) or a Portfolio position dashboard (boring).

This tool's goal is to extract tones of data in real time about the market (on any day, at any moment right now) and build up a
large corpus of live data to leverage as a feed into Machine Learning, Data Science & Statistics algorithyms...in order to support
trade strategies.

There are many websites that provide considerable data and analytics in their beautifully rich web pages, but they are slow,
over-inflated with useless bloat, riddled with targeted adds and pointless news headlines. They are unusable as a DS/ML tool for a
trader who is executing trades in real-time....but the data they show is delicious and wonderful. - That's all you really need from
their websites - their data.

So this tool's objective is to take their data, package it into internal API methods and focus it into ONE single pool of information.
<br>
<br>

**DISCLAIMER**: Most websites do not like or appreciate data scraping apps/robots or apps that treat their website as a source of raw data (by extracting data from their underlying platform). Using this App might not be well-aligned with some website usage 'Terms & conditions'.  - Caveat emptor.

Regards,<br>
**~Orville**
