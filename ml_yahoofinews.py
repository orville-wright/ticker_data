#!/home/orville/venv/devel/bin/python3
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, date
import hashlib
import re
import logging
import argparse
import time
from rich import print
from rich.markup import escape

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class yfnews_reader:
    """
    Read Yahoo Finance news reader, Word Vectorizer, Positive/Negative sentiment analyzer
    """

    # global accessors
    symbol = None           # Unique company symbol
    yfqnews_url = None      # the URL that is being worked on
    js_session = None       # main requests session
    js_resp0 = None         # HTML session get() - response handle
    js_resp2 = None         # JAVAScript session get() - response handle
    yfn_all_data = None     # JSON dataset contains ALL data
    yfn_htmldata = None     # Page in HTML
    yfn_jsdata = None       # Page in JavaScript-HTML
    yfn_jsdb = {}           # database to hold response handles from multiple js.session_get() ops
    ml_brief = []           # ML TXT matrix for Naieve Bayes Classifier pre Count Vectorizer
    ml_ingest = {}          # ML ingested NLP candidate articles
    ml_sent = None
    ul_tag_dataset = None   # BS4 handle of the <tr> extracted data
    li_superclass = None    # all possible News articles
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    nlp_x = 0
    nsoup = None            # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods
    yfn_uh = None           # global url hinter class
    url_netloc = None
    a_urlp = None
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
        self.yfn_uh = hinst
        return

##################################### 3 ############################################
# method 3
    def update_headers(self, these_headers):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)

        # HACK! to help logging() bug to handle URLs with % in string
        logging.info('%s  - set cookies/headers PATH object' % cmi_debug )
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)+"  - "+these_headers
        logging.info('%s' % cmi_debug )

        self.path = these_headers
        self.js_session.cookies.update({'path': self.path} )
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)

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
    def init_dummy_session(self, id_url):
        cmi_debug = __name__+"::"+self.init_dummy_session.__name__+".#"+str(self.yti)
        """
        NOTE: we ping 'https://www.finance.yahoo.com'
              No need for a API specific url, as this should be the FIRST get for this url. Goal is to find & extract secret cookies
        Overwrites js_resp0 - initial session handle, *NOT* the main data session handle (js_resp2)
        """

        with self.js_session.get(id_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - extract & update GOOD cookie  ' % cmi_debug )
            # self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack
            # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

###################################### 7 ###########################################
# method 8
    def do_js_get(self, idx_x):
        """
        Use JAVAScript engine to process page
        Assumes cookies have already been set up. NO cookie update done here
        ALLWAYS create a CACHE entry in js cache DB
        Return hash of url that was read
        """
        cmi_debug = __name__+"::"+self.do_js_get.__name__+".#"+str(self.yti)+"."+str(idx_x)
        logging.info( f'ml_yahoofinews::do_js_get.#{self.yti}.#{idx_x}   - URL: %s', self.yfqnews_url )

        with self.js_session.get(self.yfqnews_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp2:
            logging.info('%s    - Javascript engine processing...' % cmi_debug )
            # on scussess, raw HTML (non-JS) response is saved in Class Global accessor -> self.js_resp2
            self.js_resp2.html.render()
            # TODO: should do some get() failure testing here
            logging.info( f'%s    - JS rendered! - store JS dataset [ {idx_x} ]' % cmi_debug )
            self.yfn_jsdata = self.js_resp2.text                # store Full JAVAScript dataset TEXT page
            auh = hashlib.sha256(self.yfqnews_url.encode())     # hash the url
            aurl_hash = auh.hexdigest()
            logging.info( f'%s    - CREATED cache entry: [ {aurl_hash} ]' % cmi_debug )
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
    def do_simple_get(self, url):
        """
        get simple raw HTML data structure (data not processed by JAVAScript engine)
        NOTE: get URL is assumed to have allready been set (self.yfqnews_url)
              Assumes cookies have already been set up. NO cookie update done here
        """
        cmi_debug = __name__+"::"+self.do_simple_get.__name__+".#"+str(self.yti)+" - ">url
        logging.info( f'%s' % cmi_debug )

        with self.js_session.get(url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - Simple HTML Request get()...' % cmi_debug )
            logging.info( f'%s - Store basic HTML dataset' % cmi_debug )
            self.yfn_htmldata = self.js_resp0.text
            auh = hashlib.sha256(url.encode())     # hash the url
            aurl_hash = auh.hexdigest()
            logging.info( f'%s - CREATE cache entry: [ {aurl_hash} ]' % cmi_debug )
            self.yfn_jsdb[aurl_hash] = self.js_resp0            # create CACHE entry in jsdb !!response, not full page TEXT data !!

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )

        return aurl_hash

###################################### 8 ###########################################
# method 9
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
        logging.info( f"%s - URL Hinter state: {type(self.yfn_uh)} " % cmi_debug )
        if scan_type == 0:    # Simple HTML BS4 scraper
            logging.info( f'%s - Check urlhash cache state: {hash_state}' % cmi_debug )
        try:
            self.yfn_jsdb[hash_state]
            logging.info( f'%s - URL EXISTS in cache: {hash_state}' % cmi_debug )
            cx_soup = self.yfn_jsdb[hash_state]
            self.nsoup = BeautifulSoup(cx_soup.text, "html.parser")   # !!!! this was soup = but I have no idea where "soup" gets set
            logging.info( f'%s - set BS4 data objects' % cmi_debug )
            self.ul_tag_dataset = self.nsoup.find(attrs={"class": "mainContent yf-tnbau3"} )        # produces : list iterator
            print (f"#################################################################" )
            print (f"{self.ul_tag_dataset}" )
            print (f"#################################################################" )
            self.li_superclass = self.ul_tag_dataset.find_all(attrs={"stream-item story-item yf-1drgw51"} )
        except KeyError as error:
            logging.info( f'%s - MISSING in cache: Must read JS page' % cmi_debug )
            logging.info( f'%s - Force read news url: {self.yfqnews_url}' % cmi_debug )
            hx = self.do_js_get(bs4_obj_idx)
            logging.info( f'%s - FRESH JS page in use: [ {bs4_obj_idx} ]' % cmi_debug )
            nsoup = BeautifulSoup(self.yfn_jsdata.text, "html.parser")    # store gloabl. dont use cache object 
            logging.info( f'%s - set BS4 data objects' % cmi_debug )

            self.ul_tag_dataset = self.nsoup.find(attrs={"class": "container yf-1ce4p3e"} )        # produces : list iterator
            print ( f"#################################################################" )
            print ( f"### DEBUG: {self.ul_tag_dataset}" )
            self.li_superclass = self.ul_tag_dataset.find_all(attrs={"stream-item story-item yf-1usaaz9"} )

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
            logging.info( f'%s - Article Zone scanning / ml_ingest populating...' % cmi_debug )
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
                        uhint, uhdescr = self.yfn_uh.uhinter(hcycle, self.article_url)       # raw url string
                        logging.info( f'%s - Source url [{self.a_urlp.netloc}] / u:{uhint} / {uhdescr}' % (cmi_debug) )
                        pure_url = 1                    # explicit pure URL to remote entity
                        if uhint == 0: thint = 0.0      # Fake news / remote-stub @ YFN stub
                        if uhint == 1: thint = 1.0      # real news / local page
                        if uhint == 2: thint = 4.0      # video (currently / FOR NOW, assume all videos are locally hosted on finanice.yahoo.com
                        if uhint == 3: thint = 1.1      # shoudl never trigger here - see abive... <Pure-Abs url>
                        if uhint == 4: thint = 7.0      # research report / FOR NOW, assume all research reports are locally hosted on finanice.yahoo.com
                        if uhint == 5: thint = 6.0      # Bulk Yahoo Premium Service add
                        inf_type = self.yfn_uh.confidence_lvl(thint)  # my private look-up / returns a tuple
                        self.url_netloc = self.a_urlp.netloc      # get FQDN netloc
                        ml_atype = uhint
                        hcycle += 1
                        break
                    else:
                        self.a_url = f"https://finance.yahoo.com{self.article_url}"
                        self.a_urlp = urlparse(self.a_url)
                        self.url_netloc = self.a_urlp.netloc      # get FQDN netloc
                        logging.info( f'%s - Source url: {self.a_urlp.netloc}' % (cmi_debug) )
                        uhint, uhdescr = self.yfn_uh.uhinter(hcycle, self.a_urlp)          # urlparse named tuple
                        if uhint == 0: thint = 0.0      # real news / remote-stub @ YFN stub
                        if uhint == 1: thint = 1.0      # real news / local page
                        if uhint == 2: thint = 4.0      # video (currently / FOR NOW, assume all videos are locally hosted on finanice.yahoo.com
                        if uhint == 3: thint = 1.1      # shoudl never trigger here - see abive... <Pure-Abs url>
                        if uhint == 4: thint = 7.0      # research report / FOR NOW, assume all research reports are locally hosted on finanice.yahoo.com
                        if uhint == 5: thint = 6.0      # Bulk Yahoo Premium Service add                      
                        pure_url = 0                    # locally hosted entity
                        ml_atype = uhint                    # Real news
                        inf_type = self.yfn_uh.confidence_lvl(thint)                # return var is tuple
                        hcycle += 1
                        break       # ...need 1 more level of analysis analysis to get headline & teaser text

                print ( f"New article:      {symbol} / [ {cg} ] / Depth 1" )
                print ( f"News item:        {inf_type[0]} / Origin confidence: [ t:{ml_atype} u:{uhint} h:{thint} ]" )
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
                # ONLY insert type 0, 1 articles as NLP candidates !!
                # WARN: after interpret_page() this DICT may contain new fields i.e. 'exturl:'
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
        #cmi_debug = __name__+"::interpret_page.#"+str(self.yti)
        cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)
        #logging.info('%s - IN' % cmi_debug )
        right_now = date.today()
        idx = item_idx
        #data_row = data_row
        symbol = data_row['symbol']
        ttype = data_row['type']
        thint = data_row['thint']
        uhint = data_row['uhint']
        durl = data_row['url']
        cached_state = data_row['urlhash']

        self.this_article_url = data_row['url']
        symbol = symbol.upper()

        logging.info( f'%s - urlhash cache lookup: {cached_state}' % cmi_debug )
        cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)+" - "+durl
        logging.info( f'%s' % cmi_debug )     # hack fix for urls containg "%" break logging module (NO FIX
        #logging.info( f'ml_yahoofinews::interpret_page: - %s' % durl )     # urls containg "%" break logging module (NO FIX)
        cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)

        logging.info( f'%s - CHECKING cache... {cached_state}' % cmi_debug )
        try:
            self.yfn_jsdb[cached_state]
            cx_soup = self.yfn_jsdb[cached_state]
            logging.info( f'%s - Cached object FOUND: {cached_state}' % cmi_debug )
            dataset_1 = self.yfn_jsdata     # processed data from request.get() response
            self.nsoup = BeautifulSoup(escape(dataset_1), "html.parser")
            logging.info( f'%s - Cache BS4 object:   {type(cx_soup)}' % cmi_debug )
            logging.info( f'%s - Dataset object    : {type(dataset_1)}' % cmi_debug )
            logging.info( f'%s - Cache URL object  : {type(durl)}' % cmi_debug )
        except KeyError:
            logging.info( f'%s - MISSING from cache / must read page' % cmi_debug )
            logging.info( f'%s - Cache URL object  : {type(durl)}' % cmi_debug )
 
            cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)+" - "+durl
            logging.info( f'%s' % cmi_debug )     # hack fix for urls containg "%" break logging module (NO FIX
            #logging.info( f'ml_yahoofinews::interpret_page: - %s' % durl )     # urls containg "%" break logging module (NO FIX)
            cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)
 
            self.yfqnews_url = durl
            ip_urlp = urlparse(durl)
            ip_headers = ip_urlp.path
            self.init_dummy_session(durl)
            self.update_headers(ip_headers)

            #xhash = self.do_js_get(idx)
            xhash = self.do_simple_get(durl)             # for testing non JS Basic HTML get()
            self.yfqnews_url = durl                      # ""   ""
            logging.info( f'%s - REPEAT cache lookup for urlhash: {cached_state}' % cmi_debug )
            if self.yfn_jsdb[cached_state]:
                logging.info( f'%s - Cached object FOUND: {cached_state}' % cmi_debug )
                cy_soup = self.yfn_jsdb[cached_state]    # get() response 
                #dataset_2 = self.yfn_jsdata
                dataset_2 = self.yfn_htmldata           # for testing non JS Basic HTML get()
                logging.info ( f'%s - cache url:     {type(durl)}' % cmi_debug )
                logging.info ( f'%s - cache request: {type(cy_soup)}' % cmi_debug )
                logging.info ( f'%s - Cache dataset: {type(self.yfn_jsdata)}' % cmi_debug )
                self.nsoup = BeautifulSoup(escape(dataset_2), "html.parser")
            else:
                logging.info( f'%s - FAILED to read JS doc and set BS4 obejcts' % cmi_debug )
                return 10, 10.0, "ERROR_unknown_state!"

        
        logging.info( f'%s - set BS4 data zones for Article: [ {idx} ]' % cmi_debug )
        local_news = self.nsoup.find(attrs={"class": "body yf-3qln1o"})   # full news article - locally hosted
        #local_news = self.nsoup.find(attrs={"class": "body yf-tsvcyu"})   # full news article - locally hosted
        local_news_meta = self.nsoup.find(attrs={"class": "main yf-cfn520"})   # comes above/before article
        local_stub_news = self.nsoup.find_all(attrs={"class": "article yf-l7apfj"})
        local_story = self.nsoup.find(attrs={"class": "body yf-tsvcyu"})  # Op-Ed article - locally hosted
        local_video = self.nsoup.find(attrs={"class": "body yf-tsvcyu"})  # Video story (minimal supporting text) stub - locally hosted
        full_page = self.nsoup()  # full news article - locally hosted
        #rem_news = nsoup.find(attrs={"class": "caas-readmore"} )           # stub news article - remotely hosted


        # Depth 2.0 :Local news article / Hosted in YFN
        if uhint == 0:
                logging.info ( f"%s - Depth: 2.0 / Local Full artice / [ u: {uhint} h: {thint} ]" % cmi_debug )
                logging.info ( f'%s - Depth: 2.0 / BS4 processed doc length: {len(self.nsoup)}' % cmi_debug )
                logging.info ( f'%s - Depth: 2.0 / nsoup type is: {type(self.nsoup)}' % cmi_debug )
                
                author_zone = local_news_meta.find("div", attrs={"class": "byline-attr-author yf-1k5w6kz"} )                    
                pubdate_zone = local_news_meta.find("div", attrs={"class": "byline-attr-time-style"} )
                try:
                    author = author_zone.a.string
                except AttributeError:
                    logging.info ( f"%s - Depth: 2.0 / Author zone error:  No <A> zone - trying basic..." % cmi_debug )
                    try:
                        author = author_zone.string
                    except AttributeError:
                        logging.info ( f"%s - Depth: 2.0 / Author zone error:  No <A> zone - trying basic..." % cmi_debug )
                        author = "ERROR_author_zone"

                pubdate = pubdate_zone.time.string

                print( f"Publish INFO:  [ Author: {author} / Published: {pubdate} ]" )
                if local_news.find_all("p" ) is not None:
                #if article_zone is not None:
                    #article = article_zone
                    logging.info ( f"%s - Depth: 2.0 / GOOD <p> zone / Local full TEXT article" % cmi_debug )
                    logging.info ( f"%s - Depth: 2.0 / NLP candidate is ready" % cmi_debug )
                    #print ( f"############################ rem news #############################" )
                    #print ( f"### DEBUG:{full_page.prettify()}" )
                    #print ( f"### DEBUG:{self.nsoup.text}" )
                    #print ( f"############################ rem news #############################" )
                data_row.update({"viable": 1})                       # cab not extra text data from this article
                self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
                return uhint, thint, durl

        # Depth 2.1 : Fake local news stub / Micro article links out to externally hosted article
        if uhint == 1:
            logging.info ( f"%s - Depth: 2.1 / Fake Local news stub / [ u: {uhint} h: {thint} ]" % cmi_debug )
            logging.info ( f'%s - Depth: 2.1 / BS4 processed doc length: {len(self.nsoup)}' % cmi_debug )
            logging.info ( f'%s - Depth: 2.1 / nsoup type is: {type(self.nsoup)}' % cmi_debug )

            local_news_meta = self.nsoup.find("head")
            local_news_body = self.nsoup.find("body")
            local_news_bmain = local_news_body.find("main")
            local_news_bmart = local_news_bmain.find("article")
            local_news_bmart_divs = local_news_bmart.find_all("div")

            local_news_meta_desc = self.nsoup.find("meta", attrs={"name": "description"})

            #local_news_bmart_cap = local_news_bmart.find("div", attrs={"class": "caas-title-wrapper"})
            local_news_bmart_cap = local_news_bmart.find("div", attrs={"class": "cover-title yf-1rjrr1"})
            caption_pct_cl = re.sub(r'[\%]', "PCT", local_news_bmart_cap.text)  # cant have % in text. Problematic !!
            logging.info ( f'%s - COVER CAPTION: {caption_pct_cl}' % cmi_debug )

            #local_news_bmart_ath = local_news_bmart.find("div", attrs={"class": "caas-attr-item-author"})
            #local_news_bmart_dte = local_news_bmart.find("div", attrs={"class": "caas-attr-time-style"})

            local_news_bmart_ath = local_news_bmart.find("div", attrs={"class": "byline-attr-author yf-1k5w6kz"})
            logging.info ( f'%s - AUTHOR: {local_news_bmart_ath.text}' % cmi_debug )

            local_news_bmart_dte = local_news_bmart.find("time", attrs={"class": "byline-attr-meta-time"})
            logging.info ( f'%s - PUB TIME: {local_news_bmart_dte.text}' % cmi_debug )

            local_news_bmain_azone = local_news_bmain.find("a")

            """
            print ( f"### DEBUG - Meta tle: {local_news_meta.title.string}" )
            print ( f"### DEBUG - Meta:     {local_news_meta_desc['content']}" )
            print ( f"### DEBUG - Caption:  {local_news_bmart_cap.h1.text}" )
            print ( f"### DEBUG - Authour:  {local_news_bmart_ath.text}" )
            print ( f"### DEBUG - Date:     {local_news_bmart_dte.text}" )
            print ( f"### DEBUG - Ext link: {local_news_bmain_azone['href']}" )
            print ( f"### DEBUG - Article:  {local_news_bmain_azone.text}" )
            """
            
            """
            for i in range(0, len(local_news_bmart_divs)):
                try:
                    print ( f"zone: {i}: {local_news_bmart_divs[i]['class']}")
                    #for j in range(0, len(local_news_meta[i]['class'])):
                    #    try:
                    #        print ( f"class: {local_news_meta[i]['class'][j]}")
                    #    except KeyError:
                    #        print ( f"class: no class")
                except KeyError:
                    print ( f"zone: {i}: no zone")
                pass
            """

            author = local_news_bmart_ath.text
            pubdate = local_news_bmart_dte.text

            # f-string cannot handle % sign in strings to expand + print
            #  cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)
            cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)+" - Depth: 2.1 / Caption: "+caption_pct_cl
            #logging.info ( f"%s - Depth: 2.1 / Caption: {local_news_bmart_cap.h1.text}" % cmi_debug )
            logging.info ( f"%s" % cmi_debug )
            cmi_debug = __name__+"::"+self.interpret_page.__name__+".#"+str(item_idx)
            logging.info ( f"%s - Depth: 2.1 / Author: {author} / Published: {pubdate}" % cmi_debug )
            logging.info ( f"%s - Depth: 2.1 / External link: {local_news_bmain_azone['href']}" % cmi_debug )

            thint = 1.1
            if local_news_bmart is not None:                         # article has some content
                logging.info ( f"%s - Depth: 2.1 / Good article stub / External location @: {local_news_bmain_azone['href']}" % cmi_debug )
                ext_url_item =  local_news_bmain_azone['href']       # build a new dict entry (external; absolute url)
                logging.info ( f"%s - Depth: 2.1 / Insert url into ml_ingest: [{ext_url_item}] " % cmi_debug )
                # !! this is wrong - need to add new field exturl to the data_row dict
                #data_row.update(url = ext_url_item)                 # insert new dict entry into ml_ingest via an AUGMENTED data_row
                data_row.update({"exturl": ext_url_item})            # insert new dict entry into ml_ingest via an AUGMENTED data_row
                data_row.update({"viable": 0})                       # cab not extra text data from this article
                self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
                logging.info ( f"%s - Depth: 2.1 / NLP candidate is ready [ u: {uhint} h: {thint} ]" % cmi_debug )
                return uhint, thint, ext_url_item
            elif local_stub_news.text == "Story continues":          # local articles have a [story continues...] button
                logging.info ( f"%s - Depth: 2.1 / GOOD [story continues...] stub" % cmi_debug )
                logging.info ( f"%s - Depth: 2.1 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                data_row.update({"viable": 0})                       # cab not extra text data from this article
                self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
                return uhint, thint, self.this_article_url           # REAL local news
            elif local_story.button.text == "Read full article":     # test to make 100% sure its a low quality story
                logging.info ( f"%s - Depth: 2.1 / GOOD [Read full article] stub" % cmi_debug )
                logging.info ( f"%s - Depth: 2.1 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                data_row.update({"viable": 0})                       # cab not extra text data from this article
                self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
                return uhint, thint, self.this_article_url              # Curated Report
            else:
                logging.info ( f"%s - Depth: 2.1 / NO local page interpreter available / u: {uhint} t: {thint}" % cmi_debug )
                data_row.update({"viable": 0})                       # cab not extra text data from this article
                self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
                return uhint, 9.9, self.this_article_url
        
        if uhint == 2:
            if local_video.find('p'):          # video page only has a small <p> zone. NOT much TEXT (all the news is in the video)
                logging.info ( f'%s - Depth: 2.2 / BS4 processed doc length: {len(self.nsoup)}' % cmi_debug )
                logging.info ( f"%s - Depth: 2.2 / GOOD [Video report] minimal text" % cmi_debug )
                logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                data_row.update({"viable": 0})                       # cab not extra text data from this article
                self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
                return uhint, thint, self.this_article_url                   # VIDEO story with Minimal text article
            else:
                logging.info ( f"%s - Depth: 2.2 / ERROR failed to interpret [Video report] page" % cmi_debug )
                logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
                data_row.update({"viable": 0})                       # cab not extra text data from this article
                self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
                return uhint, 9.9, self.this_article_url                   # VIDEO story with Minimal text article

        if uhint == 3:
            logging.info ( f"%s - Depth: 2.2 / External publication - CANT interpret remote article @ [Depth 2]" % cmi_debug )
            logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
            data_row.update({"viable": 0})                       # cab no extra text data from this article
            self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
            return uhint, thint, self.this_article_url           # Explicit remote article - can't interpret off-site article

        if uhint == 4:
            logging.info ( f"%s - Depth: 2.2 / POSSIBLE Research report " % cmi_debug )
            logging.info ( f"%s - Depth: 2.2 / confidence level / u: {uhint} h: {thint}" % cmi_debug )
            data_row.update({"viable": 0})                       # cab not extra text data from this article
            self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
            return uhint, thint, self.this_article_url                      # Explicit remote article - can't see into this off-site article

        logging.info ( f"%s - Depth: 2.10 / ERROR NO page interpreter logic triggered" % cmi_debug )
        data_row.update({"viable": 0})                       # cab not extra text data from this article
        self.ml_ingest[idx] = data_row                       # now PERMENTALY update the ml_ingest record @ index = id
        return 10, 10.0, "ERROR_unknown_state!"              # error unknown state

###################################### 12 ###########################################
# method 12
    def extract_article_data(self, item_idx, sentiment_ai):
        """
        Depth 3:
        Only do this once the article has been evaluated and we knonw exactly where/what each article is
        Any article we read, should have its resp & BS4 objects cached in yfn_jsdb{}
        Set the Body Data zone, the <p> TAG zone
        Extract all of the full article raw text
        Store it in a Database
        Associate it to themetadata info for this article
        Its now available for the LLM to read and process
        """

        cmi_debug = __name__+"::"+self.extract_article_data.__name__+".#"+str(self.yti)
        logging.info( f'%s - IN / Work on item... [ {item_idx} ]' % cmi_debug )

        
        data_row = self.ml_ingest[item_idx]
        symbol = data_row['symbol']
        cached_state = data_row['urlhash']
        if 'exturl' in data_row.keys():
            durl = data_row['exturl']
            external = True
        else:
            durl = data_row['url']
            external = False

        symbol = symbol.upper()

        # TODO:
        # since this code is exact duplicate of interpret_page(), we
        # shoud make this a method and call it when needed
        # it would retrun self.nsoup and set self.yfn_jsdata
        logging.info( f'%s - urlhash cache lookup: {cached_state}' % cmi_debug )
        cmi_debug = __name__+"::"+self.extract_article_data.__name__+".#"+str(item_idx)+" - URL: "+durl
        logging.info( f'%s' % cmi_debug )     # hack fix for urls containg "%" break logging module (NO FIX
        cmi_debug = __name__+"::"+self.extract_article_data.__name__+".#"+str(item_idx)

        logging.info( f'%s - CHECKING cache... {cached_state}' % cmi_debug )
        try:
            self.yfn_jsdb[cached_state]
            cx_soup = self.yfn_jsdb[cached_state]
            logging.info( f'%s - Found cahce entry / Render data from cache...' % cmi_debug )
            #cx_soup.html.render()           # since we dont cache the raw data, we need to render the page again
            self.yfn_jsdata = cx_soup.text   # store the rendered raw data
            dataset_1 = self.yfn_jsdata
            logging.info( f'%s - Cached object    : {cached_state}' % cmi_debug )
            logging.info( f'%s - Cache req/get    : {type(cx_soup)}' % cmi_debug )
            logging.info( f'%s - Cahce Dataset    : {type(dataset_1)}' % cmi_debug )
            logging.info( f'%s - Cache URL object : {cx_soup.url}' % cmi_debug )
            self.nsoup = BeautifulSoup(escape(dataset_1), "html.parser")
        except KeyError:
            logging.info( f'%s - MISSING from cache / must read page' % cmi_debug )
            logging.info( f'%s - Cache URL object  : {type(durl)}' % cmi_debug )
 
            cmi_debug = __name__+"::"+self.extract_article_data.__name__+".#"+str(item_idx)+" - "+durl
            logging.info( f'%s' % cmi_debug )     # hack fix for urls containg "%" break logging module (NO FIX
            cmi_debug = __name__+"::"+self.extract_article_data.__name__+".#"+str(item_idx)
 
            self.yfqnews_url = durl
            ip_urlp = urlparse(durl)
            ip_headers = ip_urlp.path
            self.init_dummy_session(durl)
            self.update_headers(ip_headers)

            #xhash = self.do_js_get(item_idx)
            cy_soup = self.yfn_jsdb[cached_state]     # get() response 
            xhash = self.do_simple_get(durl)          # for testing non JS Basic HTML get()
            #self.yfqnews_url = url                   # ""   ""

            logging.info( f'%s - Retry cache lookup for: {cached_state}' % cmi_debug )
            if self.yfn_jsdb[cached_state]:
                logging.info( f'%s - Found cache entry: {cached_state}' % cmi_debug )
                #cy_soup.html.render()                  # disbale JS render()
                self.yfn_jsdata = cy_soup.text
                #dataset_2 = self.yfn_jsdata            # Javascript engine render()...slow
                dataset_2 = self.yfn_htmldata           # Basic HTML engine  get()
                logging.info ( f'%s - Cache url:     {cy_soup.url}' % cmi_debug )
                logging.info ( f'%s - Cache req/get: {type(cy_soup)}' % cmi_debug )
                logging.info ( f'%s - Cache Dataset: {type(self.yfn_jsdata)}' % cmi_debug )
                self.nsoup = BeautifulSoup(escape(dataset_2), "html.parser")
            else:
                logging.info( f'%s - FAIL to set BS4 data !' % cmi_debug )
                return 10, 10.0, "ERROR_unknown_state!"

        logging.info( f'%s - Extract ML TEXT dataset: {durl}' % (cmi_debug) )
        if external is True:    # page is Micro stub Fake news article
            logging.info( f'%s - Skipping Micro article stub... [ {item_idx} ]' % cmi_debug )
            return
            # Do not do deep data extraction
            # just use the CAPTION Teaser text from the YFN local url
            # we extracted that in interpret_page()
        else:
            logging.info( f'%s - set BS4 data zones for article: [ {item_idx} ]' % cmi_debug )
            #local_news = self.nsoup.find(attrs={"class": "body yf-tsvcyu"})             # full news article - locally hosted
            local_news = self.nsoup.find(attrs={"class": "body yf-3qln1o"})             # full news article - locally hosted
            local_news_meta = self.nsoup.find(attrs={"class": "main yf-cfn520"})        # comes above/before article
            # local_stub_news = self.nsoup.find_all(attrs={"class": "article yf-l7apfj"})
            local_stub_news = self.nsoup.find_all(attrs={"class": "body yf-3qln1o"})   # full news article - locally hosted
            local_stub_news_p = local_news.find_all("p")    # BS4 all <p> zones (not just 1)

            ####################################################################
            ##### M/L Gen AI NLP starts here !!!                         #######
            ##### Heavy CPU utilization / local LLM Model & no GPU       #######
            ####################################################################
            #
            logging.info( f'%s - Init M/L NLP Tokenizor sentiment-analyzer pipeline...' % cmi_debug )
            total_tokens, total_words, total_scent = sentiment_ai.compute_sentiment(symbol, item_idx, local_stub_news_p)
            print ( f"Total tokens generated: {total_tokens}" )
            #
            # create emtries in the Neo4j Graph database
            # - check if KG has existing node entry for this symbol+news_article
            # if not... create one
            print ( f"======================================== End: {item_idx} ===============================================")

        return total_tokens, total_words, total_scent

###################################### 13 ###########################################
# method 14
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
