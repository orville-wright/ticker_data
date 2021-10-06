# ticker_data

Date: 06 Oct 2021<br>
** Major updates **<br>
<br>
<br>
Bigcharts did a large data schema udpate to its quote zone, which broke the data extractors badly. Interstingly Bigcharts is a subsidary of marketwatch.com, which is a subsidiary of Dow Jones & Company, which is a property of News Corp (OMG). It's also odd that this schema update happened 1 week after nasdaq.com did their major data schema update. The extractors and data cleaners/wranglers are now fully updated and re-aligned with the new schema (which had some non-trivial internal changes).
<br>
NASDAQ.com did a major release of their Live Quote API data model. NASDAQ pushed their update out on Sept 31st and it became live on Oct 1. This broke a lot of quote related code as NASDAQ.com has divided their Live quote data model into multiple API zones. The fix has been completed and the code is now re-aligned with NASDAQ.com new data model (which is a bit messy under the covers as it's now 4+ API zones & has inconsistencies in the json data structures across the 4 zones).<br>
<br>
<br>
28 Sept 2021:<br>
YAHOO.com did a major rewrite of their internal page data structures (see disclaimer below). This broke the finance.yahoo.com core data scraper badly. The code is now fully aware of Yahoo's enhancments. The logic works well (again). I've started investigating the query1.yahoo.com API interface as an alternative to scraping.<br>
- The news ML (NLP) prepare functionaly (i.e. -n <symbol> and -a CMD_line options) are now stable. The NLP prep code runs without errors & the new hinter/confidence logic is complete. All this NLP pre-work code is necessary to prepare the machine to NLP read a corpus of stock news articles etc. We need to know which articles are 'Real news reports' which articels are junk adds or bogus links to junk adds, and where the final target article lives in the real world.
<br>
<br>
Older news...<br>
- ML NLP (Natural Language Processing) hacking continues - The machine wants to NLP read the news artciles for a stock and guess/inferr sentimnet.
- the NLP prep system now scans the Yahoo Finance NEWS feeds of multiple stocks and inferrs (with confidence) new articles that are fake/credible, their type & thier true locality.
- This is pretty complex (i..e deciding what a real news item is (article/reseasrch report/vide story, op-ed article etc) and then learning the final target locatlity of the article you want to the machine to NLP real. All this NLP prep-code is very finaince.yahoo.com centric, but now that its complete...it wont be difficlt to port to other news data sources.<br>
<br>
<br>
<br>
**DISCLAIMER**<br>
Tis code is still in heavy development & design. Much of it works well, but a few areas are still early in their prototyping phase (e.g. ML & A.I). Also, the overall strategy behind the design is subject to change as code in key areas becomes more functional. - Use at you own risk.<br>
<br>
**SYNOPSIS**<br>
I built this App to extract live stock data (the raw data info) from various real-time Market web feeds.<br>
It's main objectis is to literally *get at the raw underlying data*, so you can do much more interesting things with it.<br>
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

**DISCLAIMER**: Most websites do not like or appreciate data scraping apps/robots or apps that treat their website as a source of raw data (by extracting data from their underlying platform). Using this App might not be well-aligned with some website usage 'Terms & conditions'.  - Caveat emptor.<br>
<br>
This code works on production websites/pages & API that are in constant development. The data scraping and API extraction  is coded for the internal structures of each source webpage & API; at a *point-in-time*. Those pages may change at any time as the sites do updates, enhancments & optimzations. - This may result in the data extraction & data wrangeling code breaking.


Regards,<br>
**~Orville**
