#!/usr/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, date
import hashlib
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading
import json
from rich import print

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class yfnews_reader:
    """
    Read Yahoo Finance news reader, Word Vectorizer, Positive/Negative sentiment analyzer
    """

    # global accessors
    symbol = ""             # Unique company symbol
    yfqnews_url = ""        # the URL that is being worked on
    js_session = ""         # main requests session
    js_resp0 = ""           # HTML session get() - response handle
    js_resp2 = ""           # JAVAScript session get() - response handle
    yfn_all_data =""        # JSON dataset contains ALL data
    yfn_htmldata = ""       # Page in HTML
    yfn_jsdata = ""         # Page in JavaScript-HTML
    ml_brief = []           # ML TXT matrix for Naieve Bayes Classifier pre Count Vectorizer
    ml_ingest = {}          # ML ingested NLP candidate articles
    ul_tag_dataset = ""     # BS4 handle of the <tr> extracted data
    yfn_df0 = ""            # DataFrame 1
    yfn_df1 = ""            # DataFrame 2
    inst_uid = 0
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    nlp_x = 0
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods
    uh = ""                 # global url hinter class

                            # yahoo.com header/cookie hack
    yahoo_headers = { \
                    'authority': 'yahoo.com', \
                    'path': '/v1/finance/trending/US?lang=en-US&region=US&count=5&corsDomain=finance.yahoo.com', \
                    'origin': 'https://finance.yahoo.com', \
                    'referer': 'https://finance.yahoo.com/', \
                    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', \
                    'sec-ch-ua-mobile': '"?0"', \
                    'sec-fetch-mode': 'cors', \
                    'sec-fetch-site': 'cross-site', \
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' }


    def __init__(self, yti, symbol, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args
        self.symbol = symbol
        self.yti = yti
        self.nlp_x = 0
        self.cycle = 1
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.yahoo_headers)     # load cookie/header hack data set into session
        return

    def share_hinter(self, hinst):
        cmi_debug = __name__+"::"+self.share_hinter.__name__+".#"+str(self.yti)
        logging.info( f'%s - IN {type(hinst)}' % cmi_debug )
        self.uh = hinst
        return

# method #1
    def yfn_bintro(self):
        """
        DELETE ME - redundent
        Initial blind intro to yahoo.com/news JAVASCRIPT page
        NOTE: BeautifulSoup scraping required as no REST API endpoint is available.
              Javascript engine processing may be required to process/read rich meida JS page data
        """

        cmi_debug = __name__+"::"+self.yfn_bintro.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        # Initial blind get - present ourself to yahoo.com so we can extract critical cookies
        logging.info('%s - blind intro get()' % cmi_debug )
        self.js_session.cookies.update(self.yahoo_headers)    # redundent as it's done in INIT but I'm not sure its persisting from there
        with self.js_session.get("https://www.finance.yahoo.com", stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - EXTRACT/INSERT 8 special cookies  ' % cmi_debug )
            self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack

        # 2nd get with the secret yahoo.com cookies now inserted
        # NOTE: Just the finaince.Yahoo.com MAIN landing page - generic news
        logging.info('%s - rest API read json' % cmi_debug )
        with self.js_session.get("https://www.finance.yahoo.com", stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp2:
            # read the webpage with our Javascript engine processor
            logging.info('%s - Javascript engine processing disabled...' % cmi_debug )
            #self.js_resp2.html.render()    # render JS page
            logging.info('%s - Javascript engine completed!' % cmi_debug )

            # Setup some initial data structures via an authenticated/valid connection
            logging.info('%s - store FULL json dataset' % cmi_debug )
            # self.uvol_all_data = json.loads(self.js_resp2.text)
            logging.info('%s - store data 1' % cmi_debug )

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"=========================== {self.yti} / session cookies ===========================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )

        return

# method 2
    def update_headers(self, symbol):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        self.symbol = symbol
        logging.info('%s - set cookies/headers path: object' % cmi_debug )
        self.path = '/quote/' + self.symbol + '/news?p=' + self.symbol
        self.js_session.cookies.update({'path': self.path} )
        logging.info('finance.yahoo::update_headers.## - cookies/headers path: object: %s' % self.path )

        if self.args['bool_xray'] is True:
            print ( f"=========================== {self.yti} / session cookies ===========================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )

        return

# method 3
    def update_cookies(self):
        # assumes that the requests session has already been established
        cmi_debug = __name__+"::"+self.update_cookies.__name__+".#"+str(self.yti)
        logging.info('%s - REDO the cookie extract & update  ' % cmi_debug )
        self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack
        return

# method 4
    def form_url_endpoint(self, symbol):
        """
        This is the explicit NEWS URL that is used for the request get()
        NOTE: assumes that path header/cookie has been set first
        #
        URL endpoints available (examples)
        All related news        - https://finance.yahoo.com/quote/IBM/?p=IBM
        Symbol specific news    - https://finance.yahoo.com/quote/IBM/news?p=IBM
        Symbol press releases   - https://finance.yahoo.com/quote/IBM/press-releases?p=IBM
        Symbol research reports - https://finance.yahoo.com/quote/IBM/reports?p=IBM
        """

        cmi_debug = __name__+"::"+self.form_url_endpoint.__name__+".#"+str(self.yti)
        logging.info( f'%s - form URL endpoint for: {symbol}' % cmi_debug )
        self.yfqnews_url = 'https://finance.yahoo.com' + self.path    # use global accessor (so all paths are consistent)
        logging.info('finance.yahoo.com::form_api_endpoint.## - API endpoint URL: %s' % self.yfqnews_url )
        self.yfqnews_url = self.yfqnews_url
        return

# method 5
    def init_dummy_session(self):
        cmi_debug = __name__+"::"+self.init_dummy_session.__name__+".#"+str(self.yti)
        """
        NOTE: we ping finance.yahoo.com
              No need for a API specific url, as this should be the FIRST get for this url. Goal is to find & extract secret cookies
        Overwrites js_resp0 - initial session handle, *NOT* the main data session handle (js_resp2)
        """

        with self.js_session.get('https://www.finance.yahoo.com', stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - extract & update GOOD cookie  ' % cmi_debug )
            # self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack
            # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

# method 6
    def do_simple_get(self):
        """
        get simple raw HTML data structure (data not processed by JAVAScript engine)
        NOTE: get URL is assumed to have allready been set (self.yfqnews_url)
              Assumes cookies have already been set up. NO cookie update done here
        """
        cmi_debug = __name__+"::"+self.do_simple_get.__name__+".#"+str(self.yti)
        logging.info( f'%s - Simple HTML request get() on URL: {self.yfqnews_url}' % cmi_debug )
        with self.js_session.get(self.yfqnews_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - Simple HTML Request get() completed!- store HTML response dataset' % cmi_debug )
            self.yfn_htmldata = self.js_resp0.text
            # On success, HTML response is saved in Class Global accessor -> self.js_resp0
            # TODO: should do some get() failure testing here

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )

        return

# method 7
    def do_js_get(self):
        """
        get JAVAScript engine processed data structure
        NOTE: get URL is assumed to have allready been set (self.yfqnews_url)
              Assumes cookies have already been set up. NO cookie update done here
        """
        cmi_debug = __name__+"::"+self.do_js_get.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        with self.js_session.get(self.yfqnews_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp2:
            logging.info('%s - Javascript engine processing...' % cmi_debug )
            # on scussess, raw HTML (non-JS) response is saved in Class Global accessor -> self.js_resp2
            self.js_resp2.html.render()
            # TODO: should do some get() failure testing here
            logging.info('%s - Javascript engine completed! - store JS response dataset' % cmi_debug )
            self.yfn_jsdata = self.js_resp2.text    # store Full JAVAScript dataset handle

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / JS get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / JS get() session cookies ================================" )

        return

# session data extraction methods ##############################################
# method #8
    def scan_news_feed(self, symbol, depth, scan_type):
        """
        Depth 0
        1. Scan a stock symbol NEWS FEED for articles (e.g. https://finance.yahoo.com/quote/OTLY/news?p=OTLY )
        2. Evaluate the items found. Prints stats, take a HIGH-LEVEL guess at each article type (i.e. internal HTML structure).
        3. Insert NLP candidates into ml_ingest{} for deeper level 1 analysis later.
        TODO: add args - DEPTH (0, 1, 2) doesn't do anythig (yet)
        NOTE: Assumes connection/cookies/headers have previously been setup
        """
        cmi_debug = __name__+"::"+self.scan_news_feed.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        symbol = symbol.upper()
        depth = int(depth)
        logging.info( f'%s - Scan news for: {symbol} / {self.yfqnews_url}' % cmi_debug )
        logging.info( f'%s - URL hinter engine state: {type(self.uh) / {type(self.uh.uhinter)}' % cmi_debug )
        if scan_type == 0:    # Simple HTML BS4 scraper
            logging.info( '%s - Read HTML/json data using pre-init session: resp0' % cmi_debug )
            self.soup = BeautifulSoup(self.yfn_htmldata, "html.parser")
            self.ul_tag_dataset = self.soup.find(attrs={"class": "My(0) P(0) Wow(bw) Ov(h)"} )    # produces : list iterator
            # Depth 0 element zones
            #li class = where the data is hiding
            li_superclass_all = self.ul_tag_dataset.find_all(attrs={"class": "js-stream-content Pos(r)"} )
            li_superclass_one = self.ul_tag_dataset.find(attrs={"class": "js-stream-content Pos(r)"} )
            li_subset_all = self.ul_tag_dataset.find_all('li')
            li_subset_one = self.ul_tag_dataset.find('li')
            mini_headline_all = self.ul_tag_dataset.div.find_all(attrs={'class': 'C(#959595)'})
            mini_headline_one = self.ul_tag_dataset.div.find(attrs={'class': 'C(#959595)'})
        else:
            logging.info( '%s - Read JavaScript/json data using pre-init session: resp2' % cmi_debug )
            self.js_resp2.html.render()    # WARN: Assumes sucessfull JavaScript get was previously issued
            self.soup = BeautifulSoup(self.yfn_jsdata, "html.parser")
            logging.info('%s - save JavaScript-engine/json BS4 data handle' % cmi_debug )
            self.ul_tag_dataset = self.soup.find(attrs={"class": "My(0) P(0) Wow(bw) Ov(h)"} )    # TODO: might be diff for JS engine output

        logging.info( f'%s - Found: datasets: {len(self.ul_tag_dataset)}' % cmi_debug )
        logging.info( f'%s - dataset.children: {len(list(self.ul_tag_dataset.children))} / childrens.descendants: {len(list(self.ul_tag_dataset.descendants))}' % cmi_debug )

        # >>Xray DEBUG<<
        if self.args['bool_xray'] is True:
            print ( f" " )
            x = y = 1
            print ( f"=============== <li>.children / descendants ====================" )
            for child in self.ul_tag_dataset.children:
                print ( f"{x}: {child.name} / (potential good News article)" )
                y += 1
                for element in child.descendants:
                    print ( f"{y}: {element.name} ", end="" )
                    y += 1
                print ( f"\n==================== End <li> zone : {x} =========================" )
                x += 1
        print ( " " )

        return

# method #9
    def eval_article_tags(self, symbol):
        """
        Depth 1
        NOTE: assumes connection was previously setup & html data structures are pre-loaded
              leverages default JS session/request handle
              Level 0 article logic loop - we're at the TOP-level news page for this stock
        1. cycle though the top-level NEWS FEED page for this stock
        2. Scan & prepare a list of ALL of the articles we see
        3. For each article, extract KEY news elements (i.e. Headline, Brief, URL to real article)
        4. Make a high level decision as to the TYPE of item (News, paid article, Injected ad)
        5. Add articles into ml_ingest{} NLP candidate list (only types 0 & 1 are viable candidates)
        """

        cmi_debug = __name__+"::"+self.eval_article_tags.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        symbol = symbol.upper()
        li_superclass_all = self.ul_tag_dataset.find_all(attrs={"class": "js-stream-content Pos(r)"} )
        mini_headline_all = self.ul_tag_dataset.div.find_all(attrs={'class': 'C(#959595)'})
        li_subset_all = self.ul_tag_dataset.find_all('li')

        h3_counter = a_counter = 0
        x = y = 0
        pure_url = 9                                         # saftey preset
        thint = 99.9                                         # saftey preset
        uhint = 9                                            # saftey preset
        hcycle = 1
        for li_tag in li_subset_all:                         # <li> is where the new articels hide
            self.nlp_x += 1                                  # counter = which article we are looking at
            for element in li_tag.descendants:               # walk the full tag tree recurisvely
                    if element.name == "a":a_counter += 1    # can do more logic tests in here if needed
            if a_counter == 0:
                logging.info( f'%s - li count: {a_counter}' % (cmi_debug) )                  # good new zrticle found
                print ( f"Empty news page - NO NEWS found" )
                break

            if a_counter > 0 and a_counter <= 3:
                logging.info( f'%s - <li> count: {a_counter}' % (cmi_debug) )                  # good new zrticle found
                news_agency = li_tag.find(attrs={'class': 'C(#959595)'}).string
                article_url = li_tag.a.get("href")
                test_http_scheme = urlparse(article_url)
                if test_http_scheme.scheme == "https" or test_http_scheme.scheme == "http":    # check URL scheme specifier
                    logging.info ( f"%s - Depth: 1 / Pure Remote URL found!" % cmi_debug )
                    pure_url = 1    # explicit pure URL to remote entity
                    uhint = 3       # we can definatley set this here ONLY for this item type
                    url_netloc = article_url.netloc
                    ml_atype = 0
                    thint = 1.1
                else:
                    a_url = f"https://finance.yahoo.com{article_url}"
                    a_urlp = urlparse(a_url)
                    print ( f">>>DEBUG<<< parsed url: {a_urlp}" )
                    url_netloc = a_urlp.netloc      # FQDN
                    pure_url = 0                    # locally hosted entity
                    ml_atype = 0                    # Real news
                    uhint, uhdescr = self.uh.uhinter(hcycle, test_url)
                    hcycle += 1
                    # assume hosted at https://finaince.yahoo.com becasue it has no leading FQDN scheme (i.e. http/https)

                article_headline = li_tag.a.text        # taken from YFN news feed thumbnail, not actual article page
                test_url = urlparse(article_url)
                uhint, uhdescr = self.uh.uhinter(hcycle, test_url)
                hcycle += 1
                inf_type = "Real news"

                if not li_tag.find('p'):
                    url_netloc = urlparse(article_url).netloc
                    inf_type = "Micro Advertisment"
                    article_teaser = "None"
                    ml_atype = 1
                    if pure_url == 0: thint = 5.0    # local entity
                    if pure_url == 1: thint = 5.1    # remote entity
                elif news_agency == "Yahoo Finance Video" and uhint == 2:
                    thint = 4.0
                    test_url = urlparse(article_url)
                    url_netloc = test_url.netloc
                    ml_atype = 0
                else:
                    #url_netloc = "finance.yahoo.com 2"
                    url_netloc = test_url.netloc
                    a_teaser = li_tag.p.text
                    article_teaser = f"{a_teaser:.170}" + " [...]"
                    ml_atype = 0
                    if pure_url == 0: thint = 0.0
                    if pure_url == 1: thint = 1.0

                print ( f"================= Depth 1 / {symbol} Article {x} ==================" )
                print ( f"News item:        {self.cycle}: {inf_type} / Confidence Indicators t:{ml_atype}, u:{uhint}, t:{thint}" )
                print ( f"News agency:      {news_agency} / ", end="" )

                if pure_url == 0: print ( f"Remote-stub @ [ {url_netloc} ]" )
                if pure_url == 1: print ( f"Local-page  @ {url_netloc}" )
                if pure_url == 1 and uhint == 3: print ( f"Remote-external  @ {url_netloc}" )
                if uhint == 2 and thint == 4: print ( f"Local video @ {url_netloc}" )
                if pure_url == 9: print ( f"Unknown     @ *bad url*" )
                if uhint == 9: print ( f"Not yet known @ {test_url.netloc}" )

                print ( f"Article URL:      {article_url}" )
                print ( f"Article headline: {article_headline}" )
                print ( f"Article teaser:   {article_teaser}" )
                self.ml_brief.append(article_teaser)           # add Article teaser long TXT into ML pre count vectorizer matrix
                auh = hashlib.sha256(article_url.encode())
                aurl_hash = auh.hexdigest()
                print ( f"Unique url hash:  {aurl_hash}" )

                # build NLP candidate dict for deeper pre-NLP article analysis in Level 1
                # ONLY insert type 0, 1 articels as NLP candidates. Bulk injected ads are excluded (pointless)
                nd = { \
                    "symbol" : symbol,
                    "urlhash" : aurl_hash,
                    "type" : ml_atype,
                    "thint" : thint,
                    "uhint" : uhint,
                    "url" : article_url,
            		}
                self.ml_ingest.update({self.nlp_x : nd})

            else:
                found_ad = li_tag.a.text
                fa_0 = li_tag.div.find_all(attrs={'class': 'C(#959595)'})
                fa_1 = fa_0[0].get('href')
                fa_2 = fa_0[0].text
                fa_3 = fa_0[1].get('href')
                inf_type = "Bulk injected ad"
                ml_atype = 2
                thint = 6.0
                print ( f"================= Depth 1 / {symbol} Article {x} ==================" )
                print ( f"News item:        {self.cycle}: {inf_type} / Confidence > M:{ml_atype} / T:{thint}" )
                print ( f"News agency:      {fa_2} / not {symbol} news / NOT an NLP candidate" )
                print ( f"Adv injector:     {fa_3:.40} [...]" )
            a_counter = h3_counter = 0
            x += 1
            self.cycle += 1

        # need to capture junk adds here (very difficult as they're injected by add engine. Not hard page elements)
        # type = 2 / ml_atype = 2
        return

# method 10
    def get_locality(self, item_idx, data_row):
        """
        Depth 2
        Test a possible GOOD news article & return it's REAL target URL
        In the NEWs feed, 99% of news article url's are FAKE. They point to an internal stub/page
        The stub/page can have miltple personas
        1. A mini-stub, snippet of the article, "Continue" button links to a exteranly hosted article @ a partner site
        2. An artcile @ finanice.yahoo.com, shows a smippet of articel, "Continue" button opens full article on yahoo.com
        3. A fake add page on yahoo.com
        4. A fake add # a partner site
        5. other
        We must test each persona candidate article
        """
        # data elements extracted & computed
        # Authour, Date posted, Time posted, Age of article
        cmi_debug = __name__+"::"+self.get_locality.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        right_now = date.today()
        id = item_idx
        symbol = data_row['symbol']
        type = data_row['type']
        thint = data_row['thint']
        uhint = data_row['uhint']
        url = data_row['url']
        this_article_url = url
        symbol = symbol.upper()
        logging.info( f'%s - validate fake news article stub/page for: {symbol}' % (cmi_debug) )
        logging.info( f'%s - get() stub/page at URL: {this_article_url} ' % cmi_debug )
        with requests.Session() as s:
            nr = s.get( this_article_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 )
            nsoup = BeautifulSoup(nr.text, 'html.parser')
            logging.info( '%s - Stub/page has been scraped...' % cmi_debug )
            rem_news = nsoup.find(attrs={"class": "caas-readmore"})             # stub news article, remotely hosted
            local_news = nsoup.find(attrs={"class": "caas-body"})               # full news article, locally hosted
            local_story = nsoup.find(attrs={"class": "caas-body-wrapper"})      # boring options trader bland article type

            # page TYPE logic testing...
            # we test against the folling HINT codes after analyzing deeply the page structure.
            # 0 = Remote Stub
            # 1 = locally TXT articels on yahoo.com
            # 2 = locally video article on yahoo.com
            # 3 = Remote article explcitly linked directly to remote partner site
            #
            # we send back explicit type codes to indicate our confidence level in the article type
            # 0 = Good news article (remote not on yahoo.com)
            # 1 = Good news article (local, on yahoo.com)
            # 2 = OP-ED article
            # 3 = Curated report
            # 4 = Video Story
            # 5 = Micro Ad
            # 6 = Bulk Injected Ad
            # 7, 8 = (reserved and unknonw)
            # 9 = ERROR / cannot decode page structure
            # 10 = ERROR / Article URL is mangled
            #
            # return codes:
            # locality with confidence, type with confidence, rem_url of the real/physical news article

            if uhint == 0 or uhint == 1:
                print ( f">>DEBUG<< URL hint: {uhint} / Page Type hint: {thint}" )
                if type(rem_news) != type(None):               # page has valid structure
                    logging.info ( f"%s - Depth: 2 / Stub-page is valid..." % cmi_debug )
                    if rem_news.find('a'):                     # BAD, no <a> zone in page or article is a REAL remote URL already
                        rem_url = rem_news.a.get("href")       # a remotely hosted news article. Whats its real URL?
                        logging.info ( f"%s - Depth: 2 / Good <a> / Remote-stub NEWS @: {rem_url}" % cmi_debug )
                        # write the thint now
                        logging.info ( f"%s - Depth: 2 / confidence level 0 / 1.0 " % cmi_debug )
                        return uhint, 1.0, rem_url                 # 100% confidence that articel is REMOTE
                    elif rem_news.text == "Story continues":   # local articles have a [story continues...] button
                        logging.info ( f"%s - Depth: 2 / NO <a> / Good-stub [story continues...]" % cmi_debug )
                        logging.info ( f"%s - Depth: 2 / confidence level {uhint} / 0.0 " % cmi_debug )
                        return uhint, 0.0, this_article_url      # REAL news
                    elif local_story.button.text == "Read full article":    # test to make 100% sure its a low quality story
                        logging.info ( f"%s - Depth: 2 / Basic-stub [curated story]" % cmi_debug )
                        logging.info ( f"%s - Depth: 2 / confidence level {uhint} / 2.0 " % cmi_debug )
                        return uhint, 3.0, this_article_url              # Curated Report
                    else:
                        logging.info ( f"%s - Depth: 2 / NO <a> / Simple-stub [OP-ED]" % cmi_debug )
                        logging.info ( f"%s - Depth: 2 / confidence level {uhint} / 2.0 " % cmi_debug )
                        return uhint, 2.0, this_article_url          # OP-ED story (doesn't have [story continues...] button)

            if uhint == 2:
                print ( f">>DEBUG<< URL hint: {uhint} / Page Type hint: {thint}" )
                logging.info ( f"%s - Depth: 2 / NO <a> / Good-stub [Video report]" % cmi_debug )
                logging.info ( f"%s - Depth: 2 / confidence level 2 / 4.0 " % cmi_debug )
                # extract some info from the video page and do some stronger testing
                return uhint, 4.0, this_article_url          # OP-ED story (doesn't have [story continues...] button)

            if uhint == 3:
                print ( f">>DEBUG<< URL hint: {uhint} / Page Type hint: {thint}" )
                logging.info ( f"%s - Depth: 2 / Explcit Remote article" % cmi_debug )
                logging.info ( f"%s - Depth: 2 / confidence level 0 / 1.1 " % cmi_debug )
                return 1, 1.1, this_article_url              # Explicit remote article - can process any details from here

        logging.info ( f"%s - Depth: 2 / confidence level 10 / 10.0 " % cmi_debug )
        return 10, 10.0, "ERROR_unknown_state!"              # error unknown state

        """
            elif hint == 1:                                # a local YFN page, but a low quality article/report/story
                local_story.button.text == "Read full article"    # test to make 100% sure its a low quality story
                logging.info ( f"%s - Depth: 2 / Simple stub-page..." % cmi_debug )
                logging.info ( f"%s - Depth: 2 / confidence level 1 / 3 " % cmi_debug )
                return 1, 3, this_article_url              # Curated Report
            elif hint == 0:                        # definatley a REMOTE article. Cant analyze page/structure <tag> detals from here
                return 5, 0, this_article_url     # Micro Ad with pure URL pointing to physical remote article
            else:
                logging.info ( f"%s - Depth: 2 / Basic page is BAD" % cmi_debug )
                logging.info ( f"%s - Depth: 2 / confidence level 9 / -1 " % cmi_debug )
                return 9, -1, "ERROR_bad_page_struct"
        """




        """
        SAVE - good code. need to re-impliment soon - gets date/time of a good news article
        else:
            #print ( f"Tag sections in news page: {len(a_subset)}" )   # DEBUG
            for erow in range(len(a_subset)):       # cycyle through tag sections in this dataset (not predictible or consistent)
                if a_subset[erow].time:             # if this element row has a <time> tag...
                    nztime = a_subset[erow].time['datetime']
                    ndate = a_subset[erow].time.text
                    dt_ISO8601 = datetime.strptime(nztime, "%Y-%m-%dT%H:%M:%S.%fz")
                    if a_subset[erow].div:  # if this element row has a sub <div>
                        nauthor = str( "{:.15}".format(a_subset[erow].div.find(attrs={'itemprop': 'name'}).text) )
                        # nauthor = a_subset[erow].div.find(attrs={'itemprop': 'name'}).text
                        #shorten down the above data element for the pandas DataFrame insert that happens later...
                        # if self.args['bool_xray'] is True:        # DEBUG Xray
                        #    taglist = []
                        #    for tag in a_subset[erow].find_all(True):
                        #        taglist.append(tag.name)
                        #    print ( "Unique tags:", set(taglist) )
                logging.info('%s - Cycle: Follow News deep URL extratcion' % cmi_debug )
                # print ( f"Details: {ndate} / Time: {dt_ISO8601} / Author: {nauthor}" )        # DEBUG
                days_old = (dt_ISO8601.date() - right_now)
                date_posted = str(dt_ISO8601.date())
                time_posted = str(dt_ISO8601.time())
                # print ( f"News article age: DATE: {date_posted} / TIME: {time_posted} / AGE: {abs(days_old.days)}" )  # DEBUG

        return ( [nauthor, date_posted, time_posted, abs(days_old.days)] )  # return a list []
        """

# method 11
    def news_article_depth_1(self, url):
        """
        DEPRECATED - will detele soon
        Analyze 1 (ONE) individual news article taken from the list of articles for this stock.
        Set data extractor into KEY element zone within news article HTML dataset.
        Extract critical news elements, fields & data objects are full news artcile.
        Note: - called for each news article on the MAIN news page
        Note: - doing this recurisvely will be network expensive...but that is the plan
        """

        cmi_debug = __name__+"::"+self.news_article_depth_1.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        deep_url = url      # pass in the url that we want to deeply analyze
        logging.info( f'%s - Follow URL: {deep_url}' % (cmi_debug) )
        logging.info( '%s - Open/get() article data' % cmi_debug )
        with requests.Session() as s:
            nr = s.get(deep_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 )
            logging.info( f'%s - Read full HTML data with BS4: {deep_url}' % cmi_debug )
            nsoup = BeautifulSoup(nr.text, 'html.parser')
            # fake stub/page local finance.yahoo.com news artitle?
            logging.info( '%s - Check for fake local URL/Remote article URL' % cmi_debug )
            frl = nsoup.find(attrs={"class": "caas-readmore caas-readmore-collapse caas-readmore-outsidebody caas-readmore-asidepresent"})
            print ( f"{frl}" )
            y = 1
            for child in frl.children:
                print ( f"{y}: {child.name}" )
                y += 1
                for element in child.descendants:
                    print ( f"{y}: {element.name} ", end="" )
                    y += 1

            if frl.has_attr("a") is False:
                logging.info( "%s - Article HAS an <a> tag & MAYBE an <href> tag?" )
                if frl.a.get('href') == 0:    # we found a real href
                    logging.info( '%s - News article is LOCAL at finance.yahoo.com' % cmi_debug )
                    # fnl_tag_dataset = soup.find_all('a')
                    logging.info( '%s - Extract key elements/tags from HTML data' % cmi_debug )
                    tag_dataset = nsoup.div.find_all(attrs={'class': 'D(tbc)'} )
                else:
                    logging.info( '%s - Fake stub/page discovered / Article is REMOTE' % cmi_debug )
                    logging.info( f"%s - remote URL: {frl.a.get('href')}" % cmi_debug )
                    tag_dataset = 0
                    real_nurl = frl.a.get('href')    # article is REMOTE at this real location
            else:
                logging.info( "%s - Article has NO <a> or <href> tags / structure is BAD!" % cmi_debug )

            logging.info( f"%s - close news article: {deep_url}" % cmi_debug )

        return tag_dataset, real_nurl

# method 12
    def dump_ml_ingest(self):        # >>Xray DEBUG<<
        """
        Dump the contents of ml_ingest{}, which holds the NLP candidates
        """
        cmi_debug = __name__+"::"+self.dump_ml_ingest.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        print ( "================= ML Ingested Depth 1 NLP candidates ==================" )
        for k, d in self.ml_ingest.items():
            print ( f"{k:03} {d['symbol']:.5} / {d['urlhash']} Hints: [T:{d['type']} H:{d['thint']} U:{d['uhint']}] {d['url']}" )
        return
