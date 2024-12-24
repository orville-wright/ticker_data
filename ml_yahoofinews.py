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
    yfn_jsdata = "ERROR"    # Page in JavaScript-HTML
    yfn_jsdb = {}           # database to hold jsdata objects
    ml_brief = []           # ML TXT matrix for Naieve Bayes Classifier pre Count Vectorizer
    ml_ingest = {}          # ML ingested NLP candidate articles
    ul_tag_dataset = ""     # BS4 handle of the <tr> extracted data
    li_superclass = ""      # all possible News articles
    yfn_df0 = ""            # DataFrame 1
    yfn_df1 = ""            # DataFrame 2
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    nlp_x = 0
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods
    uh = ""                 # global url hinter class
    url_netloc = ""
    a_urlp = ""
    article_url = "https://www.defaul_instance_url.com"
    this_article_url = "https://www.default_interpret_page_url.com"

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
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
                    }

    def __init__(self, yti, symbol, global_args):
        self.yti = yti
        cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(self.yti)
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args
        self.symbol = symbol
        self.nlp_x = 0
        self.cycle = 1
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.yahoo_headers)     # load cookie/header hack data set into session
        self.a_urlp = urlparse('https://www.dummyurl.com')
        self.url_netloc = self.a_urlp.netloc
        return

##################################### 1 ############################################
# method 1
    def share_hinter(self, hinst):
        cmi_debug = __name__+"::"+self.share_hinter.__name__+".#"+str(self.yti)
        logging.info( f'%s - IN {type(hinst)}' % cmi_debug )
        self.uh = hinst
        return

##################################### 3 ############################################
# method 3
    def update_headers(self, symbol):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        self.symbol = symbol
        logging.info('%s - set cookies/headers path: object' % cmi_debug )
        self.path = '/quote/' + self.symbol + '/news?p=' + self.symbol
        self.js_session.cookies.update({'path': self.path} )
        logging.info( f"%s - set cookies/headers path: {self.path}" % cmi_debug )

        if self.args['bool_xray'] is True:
            print ( f"=========================== {self.yti} / session cookies ===========================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )

        return

###################################### 4 ###########################################
# method 4
    def update_cookies(self):
        # assumes that the requests session has already been established
        cmi_debug = __name__+"::"+self.update_cookies.__name__+".#"+str(self.yti)
        logging.info('%s - REDO the cookie extract & update  ' % cmi_debug )
        self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack
        return

###################################### 5 ###########################################
# method 5
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
        logging.info( f"%s - form URL endpoint for: {symbol}" % cmi_debug )
        self.yfqnews_url = 'https://finance.yahoo.com' + self.path    # use global accessor (so all paths are consistent)
        logging.info( f"%s - API endpoint URL: {self.yfqnews_url}" % cmi_debug )
        self.yfqnews_url = self.yfqnews_url
        return

###################################### 6 ###########################################
# method 6
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

###################################### 7 ###########################################
# method 8
    def do_js_get(self, idx_x):
        """
        get JAVAScript engine processed data structure
        NOTE: URL must be set before in (self.yfqnews_url)
              Assumes cookies have already been set up. NO cookie update done here
            ALLWAYS create a CACHE entry in js cache DB
            Return hash of url that was read
        """
        cmi_debug = __name__+"::"+self.do_js_get.__name__+".#"+str(self.yti)+"."+str(idx_x)
        logging.info('%s - IN' % cmi_debug )
        
        logging.info( f'%s - url: {self.yfqnews_url}' % cmi_debug )
        with self.js_session.get(self.yfqnews_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp2:
            logging.info('%s - Javascript engine processing...' % cmi_debug )
            # on scussess, raw HTML (non-JS) response is saved in Class Global accessor -> self.js_resp2
            self.js_resp2.html.render()
            # TODO: should do some get() failure testing here
            logging.info( f'%s - JS rendered! - store JS dataset [ {idx_x} ]' % cmi_debug )
            self.yfn_jsdata = self.js_resp2.text                # store Full JAVAScript dataset TEXT page
            auh = hashlib.sha256(self.yfqnews_url.encode())     # hash the url
            aurl_hash = auh.hexdigest()
            logging.info( f'%s - CREATE cache entry: [ {aurl_hash} ]' % cmi_debug )
            self.yfn_jsdb[aurl_hash] = self.js_resp2            # create CACHE entry in jsdb !! just response, not full page TEXT data !!

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / JS get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / JS get() session cookies ================================" )

        return aurl_hash

###################################### 7 ###########################################
# Possibly DEPRICATED - Delete me ?
    def do_simple_get(self):
        """
        get simple raw HTML data structure (data not processed by JAVAScript engine)
        NOTE: get URL is assumed to have allready been set (self.yfqnews_url)
              Assumes cookies have already been set up. NO cookie update done here
        """
        cmi_debug = __name__+"::"+self.do_simple_get.__name__+".#"+str(self.yti)
        logging.info( f'%s - url: {self.yfqnews_url}' % cmi_debug )

        with self.js_session.get(self.yfqnews_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - Simple HTML Request get()...' % cmi_debug )
            self.yfn_htmldata = self.js_resp0.text
            auh = hashlib.sha256(self.yfqnews_url.encode())     # hash the url
            aurl_hash = auh.hexdigest()
            logging.info( f'%s - CREATE cache entry: [ {aurl_hash} ]' % cmi_debug )
            self.yfn_jsdb[aurl_hash] = self.js_resp0            # create CACHE entry in jsdb !! just response, not full page TEXT data !!

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )

        return

###################################### 8 ###########################################
# method 9
# session data extraction methods
    def scan_news_feed(self, symbol, depth, scan_type, bs4_obj_idx, hash_state):
        """
        Depth 0 : Surface scan of all news articles in the news section for a stock ticker
        Scan_type:  0 = html | 1 = Javascript render engine
        Scan a stock symbol NEWS FEED for articles (e.g. https://finance.yahoo.com/quote/OTLY/news?p=OTLY )
        Share class accessors of where the New Articles live i.e. the <li> section
        """
        cmi_debug = __name__+"::"+self.scan_news_feed.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        symbol = symbol.upper()
        depth = int(depth)
        
        logging.info( f'%s - Scan news for: {symbol} / {self.yfqnews_url}' % cmi_debug )
        logging.info( f"%s - URL Hinter state: {type(self.uh)} " % cmi_debug )
        if scan_type == 0:    # Simple HTML BS4 scraper
            logging.info( f'%s - Check urlhash cache state: {hash_state}' % cmi_debug )
        try:
            self.yfn_jsdb[hash_state]
            logging.info( f'%s - URL EXISTS in cache: {hash_state}' % cmi_debug )
            cx_soup = self.yfn_jsdb[hash_state]
            soup = BeautifulSoup(cx_soup.text, "html.parser")
            logging.info( f'%s - set BS4 data objects' % cmi_debug )
            self.ul_tag_dataset = soup.find(attrs={"class": "container yf-1ce4p3e"} )        # produces : list iterator
            self.li_superclass = self.ul_tag_dataset.find_all(attrs={"stream-item story-item yf-1usaaz9"} )
        except KeyError as error:
            logging.info( f'%s - MISSING in cache: Must read JS page' % cmi_debug )
            logging.info( f'%s - Force read news url: {self.yfqnews_url}' % cmi_debug )
            #with requests.Session() as s:
            #    nr = s.get( self.this_article_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 )
            #    nsoup = BeautifulSoup(nr.text, 'html.parser')
            hx = self.do_js_get(bs4_obj_idx)
            logging.info( f'%s - FRESH JS page in use: [ {bs4_obj_idx} ]' % cmi_debug )
            nsoup = BeautifulSoup(self.yfn_jsdata.text, "html.parser")    # store gloabl. dont use cache object 
            logging.info( f'%s - set BS4 data objects' % cmi_debug )

            self.ul_tag_dataset = soup.find(attrs={"class": "container yf-1ce4p3e"} )        # produces : list iterator
            print ( f"#################################################################" )
            print ( f"### DEBUG: \n{self.ul_tag_dataset}" )
            self.li_superclass = self.ul_tag_dataset.find_all(attrs={"stream-item story-item yf-1usaaz9"} )

            # Depth 0 element zones
            # <li classis> is ZONE where the News Items data is hiding
            #li_superclass = self.ul_tag_dataset.find_all("ul")
            #li_subset_all = self.ul_tag_dataset.find_all('li')
            #self.js_resp2.html.render()    # WARN: Assumes sucessfull JavaScript get was previously issued

        logging.info( f'%s - Depth: 0 / Found News containers: {len(self.ul_tag_dataset)}' % cmi_debug )
        logging.info( f'%s - Depth: 0 / Found Sub cotainers:   {len(list(self.ul_tag_dataset.children))} / Tags: {len(list(self.ul_tag_dataset.descendants))}' % cmi_debug )
        logging.info( f'%s - Depth: 0 / Found News Articles:   {len(self.li_superclass)}' % cmi_debug)
 
        # >>Xray DEBUG<<
        if self.args['bool_xray'] is True:
            print ( f" " )
            x = y = 1
            print ( f"=============== <li> zone : {x} children+descendants ====================" )
            for child in self.li_superclass:
                if child.name is not None:
                    print ( f"Zone: {x}: {child.h3.text} / (potential News article)" )
                    y += 1
                    """
                    for element in child.descendants:
                        print ( f"{y}: {element.name} ", end="" )
                        y += 1
                    """
                    print ( f"==================== End <li> zone : {x} =========================" )
                    x += 1
                else:
                    print ( f"Zone: {x}: Empty no article data" )
                    print ( f"\n==================== End <li> zone : {x} =========================" )
 
        return

###################################### 9 ###########################################
# method 10
    def eval_news_feed_stories(self, symbol):
        """
        Depth 1 - scanning news feed stories and some metatdata (depth 1)
        INFO: we are NOT looking deeply inside each metat data article (depth 1) yet
        NOTE: assumes connection was previously setup & html data structures are pre-loaded
              leverages default JS session/request handle
              Depth 1 -Iinterrogate items within the main [News Feed page]
        1. cycle though the top-level NEWS FEED page for this stock
        2. Scan each article found
        3. For each article, extract KEY news elements (i.e. Headline, Brief, local URL, remote UIRL)
        4. leverage the URL hinter. Make a decision on TYPE & HINTER results
        5. Decide worthness of REAL news articles & insert into ml_ingest{} NLP candidate list
        6. Exreact some key info
        7. Create a Candidate list of articles in [ml_ingest] array 
        """

        cmi_debug = __name__+"::"+self.eval_news_feed_stories.__name__+".#"+str(self.yti)
        logging.info('%s - IN \n' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        symbol = symbol.upper()
        li_superclass_all = self.ul_tag_dataset.find_all(attrs={"class": "js-stream-content Pos(r)"} )
        mini_headline_all = self.ul_tag_dataset.div.find_all(attrs={'class': 'C(#959595)'})
        li_subset_all = self.ul_tag_dataset.find_all('li')

        h3_counter = a_counter = 0
        x = 1
        y = 0
        hcycle = 1
        pure_url = 9                                         # saftey preset
        uhint = 9                                            # saftey preset
        thint = 99.9                                         # saftey preset
        self.article_teaser ="ERROR_default_data_0"
        ml_atype = 0

        ##hacking 
        # # soup.find_all("a", attrs={"class": "sister"})
        # ('a[href]')

        ## GENERATOR: Scan & find critical tags
        def atag_gen():                         #  extract <h3>, agency, author, publish date
            a_counter = 0
            for li_tag in self.li_superclass:   # BS4 object set from scan_news_feed()
                self.nlp_x += 1
                for element in li_tag.descendants:
                    if element.name == "a":
                        a_counter += 1
                        if element.h3 is not None:
                            yield ( f"{a_counter}")
                            yield ( f"{element.h3.text}" )
                            if element.has_attr('href') is True:
                                #yield ( f'ZONE : {a_counter} : H3URL : {element.get("href")}' )
                                yield ( f'{element.get("href")}' )
                                news_ag = li_tag.find(attrs={'class': 'publishing yf-1weyqlp'}) 
                                if news_ag is not None:
                                    news_ag = news_ag.text.split("•")
                                    yield ( f"{news_ag[0]}")
                                else:
                                    yield ( f"Failed to extract News Agency" )

        ########## end Generatior

        scan_a_zone = atag_gen()
        try:
            cg = 1
            news_agency ="ERROR_default_data_1"
            while True:
                li_a_zone = next(scan_a_zone)
                self.article_teaser = next(scan_a_zone)
                print ( f"================== Article: [ {cg} ] / A-Zone: [ {li_a_zone} ] ==================" )
                self.article_url = next(scan_a_zone)
                self.a_urlp = urlparse(self.article_url)
                news_agency = next(scan_a_zone)
                inf_type = "Undefined"

                for safety_cycle in range(1):    # ABUSE for/loop BREAK as logic control exit (poor mans switch/case)
                    if self.a_urlp.scheme == "https" or self.a_urlp.scheme == "http":    # check URL scheme specifier
                        uhint, uhdescr = self.uh.uhinter(hcycle, self.article_url)       # raw url string
                        logging.info( f'%s - Source url [{self.a_urlp.netloc}] / u:{uhint} / {uhdescr}' % (cmi_debug) )
                        pure_url = 1                    # explicit pure URL to remote entity
                        if uhint == 0: thint = 0.0      # Fake news / remote-stub @ YFN stub
                        if uhint == 1: thint = 1.0      # real news / local page
                        if uhint == 2: thint = 4.0      # video (currently / FOR NOW, assume all videos are locally hosted on finanice.yahoo.com
                        if uhint == 3: thint = 1.1      # shoudl never trigger here - see abive... <Pure-Abs url>
                        if uhint == 4: thint = 7.0      # research report / FOR NOW, assume all research reports are locally hosted on finanice.yahoo.com
                        inf_type = self.uh.confidence_lvl(thint)  # my private look-up / returns a tuple
                        self.url_netloc = self.a_urlp.netloc      # get FQDN netloc
                        ml_atype = uhint
                        hcycle += 1
                        break
                    else:
                        self.a_url = f"https://finance.yahoo.com{self.article_url}"
                        self.a_urlp = urlparse(self.a_url)
                        self.url_netloc = self.a_urlp.netloc      # get FQDN netloc
                        logging.info( f'%s - Source url: {self.a_urlp.netloc}' % (cmi_debug) )
                        uhint, uhdescr = self.uh.uhinter(hcycle, self.a_urlp)          # urlparse named tuple
                        if uhint == 0: thint = 0.0      # real news / remote-stub @ YFN stub
                        if uhint == 1: thint = 1.0      # real news / local page
                        if uhint == 2: thint = 4.0      # video (currently / FOR NOW, assume all videos are locally hosted on finanice.yahoo.com
                        if uhint == 3: thint = 1.1      # shoudl never trigger here - see abive... <Pure-Abs url>
                        if uhint == 4: thint = 7.0      # research report / FOR NOW, assume all research reports are locally hosted on finanice.yahoo.com
                        pure_url = 0                    # locally hosted entity
                        ml_atype = uhint                    # Real news
                        inf_type = self.uh.confidence_lvl(thint)                # return var is tuple
                        hcycle += 1
                        break       # ...need 1 more level of analysis analysis to get headline & teaser text

                print ( f"New article:      {symbol} / [ {cg} ] / Depth 1" )
                print ( f"News item:        {self.cycle}: {inf_type[0]} / Origin confidence: [ t:{ml_atype} u:{uhint} h:{thint} ]" )
                print ( f"News agency:      {news_agency}" )
                print ( f"News origin:      {self.url_netloc}" )
                print ( f"Article URL:      {self.article_url}" )
                #print ( f"Article headline: {article_headline}" )
                print ( f"Article teaser:   {self.article_teaser}" )

                self.ml_brief.append(self.article_teaser)           # add Article teaser long TXT into ML pre count vectorizer matrix
                auh = hashlib.sha256(self.article_url.encode())     # hash the url
                aurl_hash = auh.hexdigest()
                print ( f"Unique url hash:  {aurl_hash}" )
                print ( f" " )

                # build NLP candidate dict for deeper pre-NLP article analysis in Level 1
                # ONLY insert type 0, 1 articels as NLP candidates. Bulk injected ads are excluded (pointless)
                nd = {
                    "symbol" : symbol,
                    "urlhash" : aurl_hash,
                    "type" : ml_atype,
                    "thint" : thint,
                    "uhint" : uhint,
                    "url" : self.a_urlp.scheme+"://"+self.a_urlp.netloc+self.a_urlp.path
                }
                logging.info( f'%s - Add to ML Ingest DB: [ {cg} ]' % (cmi_debug) )
                self.ml_ingest.update({self.nlp_x : nd})
                cg += 1

        except StopIteration:
            pass

        return

    """
        ################## key logic decisions made below ###################

            else:
                found_ad = li_tag.a.text
                fa_0 = li_tag.div.find_all(attrs={'class': 'C(#959595)'})
                fa_1 = fa_0[0].get('href')
                fa_2 = fa_0[0].text
                fa_3 = fa_0[1].get('href')
                inf_type = "Bulk injected ad"
                ml_atype = 2
                thint = 6.0
                print ( f"================= Article {x} / {symbol} / Depth 1 ==========================" )
                print ( f"News item:        {self.cycle}: {inf_type} / Origin Conf Indctrs [ t:{ml_atype} u:- h:{thint} ]" )
                print ( f"News agency:      {fa_2} / not {symbol} news / NOT an NLP candidate" )
                print ( f"Adv injector:     {fa_3:.40} [...]" )
            a_counter = h3_counter = 0
            x += 1
            self.cycle += 1

        return
    """

###################################### 11 ###########################################
# method 11
    def interpret_page(self, item_idx, data_row):
        """
        Depth 2 Page interpreter
        Look INSIDE each page and translate it. Test for known pages types (e.g. good news articles etc)
        Return some info that allows us to definatively know what we're looking at and how/where to NLP read the text of the artcile.
        NOTE: In the NEWs feed, 99% of news article url's are FAKE internal stubs, that point to themself or an external remote site/page.
        The stub/page can have miltple personas, so this translater is where the mahic happens...
        1. A mini-stub, snippet of the article, "Continue" button links to a exteranly hosted article @ a partner site
        2. An artcile @ finanice.yahoo.com, shows a smippet of articel, "Continue" button opens full article on yahoo.com
        3. A fake add page on yahoo.com
        4. A fake add # a partner site
        5. other
        """

        # data elements extracted & computed
        # Authour, Date posted, Time posted, Age of article
        cmi_debug = __name__+"::interpret_page.#"+str(self.yti)
        #logging.info('%s - IN' % cmi_debug )
        right_now = date.today()
        idx = item_idx
        data_row = data_row
        symbol = data_row['symbol']
        ttype = data_row['type']
        thint = data_row['thint']
        uhint = data_row['uhint']
        url = data_row['url']
        cached_state = data_row['urlhash']

        self.this_article_url = url
        symbol = symbol.upper()

        logging.info( f'%s - Check urlhash cache state: {cached_state}' % cmi_debug )
        try:
            cx_soup = self.yfn_jsdb[cached_state]
            logging.info( f'%s - EXISTS in cache: {cached_state}' % cmi_debug )
            dataset_1 = self.yfn_jsdata
            logging.info( f'%s - cache holds oject type:   {type(cx_soup)}' % cmi_debug )
            logging.info( f'%s - Dataset holds oject type: {type(dataset_1)}' % cmi_debug )
            nsoup = BeautifulSoup(dataset_1, "html.parser")
            #self.ul_tag_dataset = soup.find(attrs={"class": "container yf-1ce4p3e"} )        # produces : list iterator
            #self.li_superclass = self.ul_tag_dataset.find_all(attrs={"stream-item story-item yf-1usaaz9"} )
        except KeyError as error:
            logging.info( f'%s - MISSING in cache: Must read JS page' % cmi_debug )
            logging.info( f'%s - Force read news url: {url}' % cmi_debug )
            #with requests.Session() as s:
            #    nr = s.get( self.this_article_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 )
            #    nsoup = BeautifulSoup(nr.text, 'html.parser')
            self.yfqnews_url = url
            self.do_js_get(idx)
            logging.info( f'%s - REPEAT check for urlhash in cache: {cached_state}' % cmi_debug )
            if self.yfn_jsdb[cached_state]:
                logging.info( f'%s - EXISTS in cache: {cached_state}' % cmi_debug )
                cy_soup = self.yfn_jsdb[cached_state]
                dataset_2 = self.yfn_jsdata
                logging.info( f'%s - cache holds oject type:   {type(cy_soup)}' % cmi_debug )
                logging.info( f'%s - Dataset holds oject type: {type(dataset_2)}' % cmi_debug )
                print ( f"############################### debug ################################" )
                print ( f"### DEBUG: \n {cy_soup.html}" )
                print ( f"################################ END #################################" )
                nsoup = BeautifulSoup(dataset_2, "html.parser")
            else:
                logging.info( f'%s - FAILED to read JS doc and set BS4 obejcts' % cmi_debug )
                return 10, 10.0, "ERROR_unknown_state!"

        
        logging.info( f'%s - set BS4 data zones for Article: [ {idx} ]' % cmi_debug )
        local_news = nsoup.find(attrs={"class": "body yf-tsvcyu"})   # full news article - locally hosted
        local_news_meta = nsoup.find(attrs={"class": "main yf-cfn520"})   # comes above/before article
        local_stub_news = nsoup.find_all(attrs={"class": "article yf-l7apfj"})
        local_story = nsoup.find(attrs={"class": "body yf-tsvcyu"})  # Op-Ed article - locally hosted
        local_video = nsoup.find(attrs={"class": "body yf-tsvcyu"})  # Video story (minimal supporting text) stub - locally hosted
        full_page = nsoup()  # full news article - locally hosted
        #rem_news = nsoup.find(attrs={"class": "caas-readmore"} )           # stub news article - remotely hosted


        
        if uhint == 0:
                logging.info ( f"%s - Depth: 2.0 / Local Full artice / [ u: {uhint} h: {thint} ]" % cmi_debug )
                logging.info( f'%s - Depth: 2.0 / BS4 processed doc length: {len(nsoup)}' % cmi_debug )
                author_zone = local_news_meta.find("div", attrs={"class": "byline-attr-author yf-1k5w6kz"} )                    
                pubdate_zone = local_news_meta.find("div", attrs={"class": "byline-attr-time-style"} )
                author = author_zone.string
                pubdate = pubdate_zone.time.string
                logging.info ( f"%s - Depth: 2.0 / Extracted Author & Pub dates from article" % cmi_debug )
                logging.info ( f"%s - Depth: 2.0 / Author: {author} / Published: {pubdate}" % cmi_debug )
                article_zone = local_news.find_all("p" )
                if article_zone is not None:
                #if local_news.find('p'):                     # <p> is where the ENTIRE article is written
                    #article = article_zone
                    logging.info ( f"%s - Depth: 2.0 / GOOD <p> zone / Local full TEXT article" % cmi_debug )
                    #pub_clean = pubdate.text.lstrip()
                    #published = pub_clean.split('·', 1)
                    #author_clean = author.text.lstrip()
                    logging.info ( f"%s - Depth: 2.0 / NLP candidate is ready" % cmi_debug )
                    return uhint, thint, url
            
        # Fake local news stub / Micro article links out to externally hosted article
        if uhint == 1:
            logging.info ( f"%s - Depth: 2.1 / Fake Local news stub / [ u: {uhint} h: {thint} ]" % cmi_debug )
            #rem_news = nsoup.find(attrs={"class": "article-wrap no-bb"})
            logging.info( f'%s - Depth: 2.1 / BS4 processed doc length: {len(nsoup)}' % cmi_debug )

            #print ( f"############################ rem news #############################" )
            #print ( f"### DEBUG:\n{nsoup.prettify()}" )

            # follow link into page & read
            author_zone = local_news_meta.find("div", attrs={"class": "byline-attr-author yf-1k5w6kz"} )
            pubdate_zone = local_news_meta.find("div", attrs={"class": "byline-attr-time-style"} )
            author = author_zone.string
            pubdate = pubdate_zone.time.string

            logging.info ( f"%s - Depth: 2.1 / Extracted Author & Pub dates from article" % cmi_debug )
            logging.info ( f"%s - Depth: 2.1 / Author: {author} / Published: {pubdate}" % cmi_debug )
            rem_article_zone = local_stub_news.find_all("p")
            rem_article = rem_article_zone.p.string
            if local_stub_news.find('a'):                     # BAD, no <a> zone in page or article is a REAL remote URL already
                rem_url = local_stub_news.a.get("href")
                # Fake local news stub article, points to a remotely  news article external URL, Also has [Continue reading] button TEXT
                logging.info ( f"%s - Depth: 2.1 / Good <a> Remote-stub / News article @: {rem_url}" % cmi_debug )
                logging.info ( f"%s - Depth: 2.1 / Insert ext url into ml_ingest" % cmi_debug )
                ext_url_item = {'exturl': rem_url }     # build a new dict entry (external; absolute url)
                data_row.update(ext_url_item )          # insert new dict entry into ml_ingest via an AUGMENTED data_row
                self.ml_ingest[idx] = data_row          # now PERMENTALY update the ml_ingest record @ index = id
                logging.info ( f"%s - Depth: 2.1 / NLP candidate is ready" % cmi_debug )
                return uhint, thint, rem_url
            elif local_stub_news.text == "Story continues":         # local articles have a [story continues...] button
                logging.info ( f"%s - Depth: 2.1 / GOOD [story continues...] stub" % cmi_debug )
                logging.info ( f"%s - Depth: 2.1 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                return uhint, thint, self.this_article_url      # REAL local news
                #
            elif local_story.button.text == "Read full article":    # test to make 100% sure its a low quality story
                logging.info ( f"%s - Depth: 2.1 / GOOD [Read full article] stub" % cmi_debug )
                logging.info ( f"%s - Depth: 2.1 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                return uhint, thint, self.this_article_url              # Curated Report
                #
            else:
                logging.info ( f"%s - Depth: 2.1 / NO local page interpreter available / u: {uhint} t: {thint}" % cmi_debug )
                return uhint, 9.9, self.this_article_url
                #else:
                # still need to catch OP-ED...which is similar to [story continues...] and [Read full article]
                #    logging.info ( f"%s - Depth: 2 / NO <a> / Simple-stub [OP-ED]" % cmi_debug )
                #    logging.info ( f"%s - Depth: 2 / confidence level {uhint} / 2.0 " % cmi_debug )
                #    return uhint, 2.0, self.this_article_url          # OP-ED story (doesn't have [story continues...] button)

        if uhint == 2:
            if local_video.find('p'):          # video page only has a small <p> zone. NOT much TEXT (all the news is in the video)
                logging.info ( f'%s - Depth: 2.2 / BS4 processed doc length: {len(nsoup)}' % cmi_debug )
                logging.info ( f"%s - Depth: 2.2 / GOOD [Video report] minimal text" % cmi_debug )
                logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                return uhint, thint, self.this_article_url                   # VIDEO story with Minimal text article
            else:
                logging.info ( f"%s - Depth: 2.2 / ERROR failed to interpret [Video report] page" % cmi_debug )
                logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                return uhint, 9.9, self.this_article_url                   # VIDEO story with Minimal text article

        if uhint == 3:
            logging.info ( f"%s - Depth: 2.2 / External publication - CANT interpret remote article @ [Depth 2]" % cmi_debug )
            logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
            return uhint, thint, self.this_article_url                      # Explicit remote article - can't interpret off-site article

        if uhint == 4:
            logging.info ( f"%s - Depth: 2.2 / POSSIBLE Research report " % cmi_debug )
            logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
            # TODO:
            # test the target url? is it a finance.yahoo.com hosted research report?
            # if yes...we can interpret the page. There's lots of text data in that page...
            # e.g. https://finance.yahoo.com/research/reports/MS_0P0000XWEY_AnalystReport_1632872327000
            return uhint, thint, self.this_article_url                      # Explicit remote article - can't see into this off-site article

        logging.info ( f"%s - Depth: 2.10 / ERROR NO page interpreter logic triggered" % cmi_debug )
        return 10, 10.0, "ERROR_unknown_state!"              # error unknown state


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

###################################### 12 ###########################################
# method 12
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

###################################### 13 ###########################################
# method 13
    def dump_ml_ingest(self):        # >>Xray DEBUG<<
        """
        Dump the contents of ml_ingest{}, which holds the NLP candidates
        """
        cmi_debug = __name__+"::"+self.dump_ml_ingest.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        print ( "================= ML Ingested Depth 1 NLP candidates ==================" )
        for k, d in self.ml_ingest.items():
            print ( f"{k:03} {d['symbol']:.5} / {d['urlhash']} Hints: t:{d['type']} u:{d['uhint']} h:{d['thint']}]" )
            if 'exturl' in d.keys():
                print ( f"          Local:    {d['url']}" )
                print ( f"          External: {d['exturl']}" )
            else:
                print ( f"          Local:    {d['url']}" )

        return


##################################### 2 ############################################
# method 2
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
