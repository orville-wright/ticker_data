#!/usr/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, date
import json
import logging
import argparse
from rich import print

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class cookie_monster:
    """
    manage Yahoo cookie monster for everyone
    """

    # global class accessors
    yti = 0                 # Unique instance identifier
    jorh = 9                # which engine rendered the page : 0 = sime html / 1 Javascript render engine / 9 = unset
    cycle = 0               # class thread loop counter
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods
    a_urlp = ""             # a url
    dummy_url = "https://finance.yahoo.com"   # url for the Dummy session
    path = ""               # the path component of our url : /screener/predefined/small_cap_gainers/
    yf_htmldata = ""        # live HTML data text from a sucecssful html get()
    yf_jsdata = ""          # live JAVASCRIPT page data - NOT the HTML down rendered page
    js_resp0 = ""           # dummy html get() - response handle from a simple HTML get() - no JAVASCRIPT engine
    js_resp1 = ""           # HTML engine - response handle from a real live HTML get()
    js_resp2= ""            # JAVASCRIPT engine - response handle from a real live Javascript get()
                            # header struct
    yahoo_headers = { \
                        'authority': 'finance.yahoo.com', \
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', \
                        'path': '/markets/stocks/most-active/', \
                        'referer': 'https://finance.yahoo.com/stocks', \
                        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', \
                        'sec-ch-ua-mobile': '"?0"', \
                        'sec-fetch-mode': 'navigate', \
                        'sec-fetch-user': '"?1', \
                        'sec-fetch-site': 'same-origin', \
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' }

#######################################################################
# init
    def __init__(self, yti, path, global_args):
        self.yti = yti
        cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(self.yti)
        logging.info( f'%s - Instance.#{yti}' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args
        self.path = path
        self.cycle = 1
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.html_session = requests.Session()                 # init HTML session
        self.js_session.cookies.update(self.yahoo_headers)     # load basic cookie/header hack data set into session
        self.a_urlp = urlparse('https://www.dummyurl.com')     # ??
        return
    
#######################################################################
# method 1
    def form_url_endpoint(self):
        """
        NOTE: assumes that path header/cookie has been set first
/screener/predefined/day_gainers/        /screener/predefined/small_cap_gainers/
        /quote/IBM/?p=IBM
        /quote/IBM/press-releases?p=IBM
        """

        cmi_debug = __name__+"::"+self.form_url_endpoint.__name__+".#"+str(self.yti)
        logging.info( f"%s - form URL endpoint..." % cmi_debug )
        #self.a_urlp = 'https://finance.yahoo.com' + self.path    # use global accessor (so all paths are consistent)
        self.a_urlp = self.path                                   # use global accessor (so all paths are consistent
        logging.info( f"%s - URL endpoint: {self.a_urlp}" % cmi_debug )
        return

#######################################################################
# method 2
    def update_headers(self):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info( f"%s - insert cookie/header :path: object..." % cmi_debug )
        self.js_session.cookies.update({'path': self.path} )
        logging.info( f"%s - :path: cookie - [ {self.path} ]" % cmi_debug )

        if self.args['bool_xray'] is True:
            print ( f"========================= {self.yti} / Updated session headers ============================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================================= end =============================================\n" )
            
        return

#######################################################################
# method 3
    def init_dummy_session(self, type_of_get):
        cmi_debug = __name__+"::"+self.init_dummy_session.__name__+".#"+str(self.yti)
        """
        NOTE: we ping finance.yahoo.com
              No API specific url needed. 1st get  does need it. - Goal is to find & extract secret cookies
        Overwrites js_resp0 - initial session handle, *NOT* the main data session handle (js_resp2)
        """
        # https://query1.finance.yahoo.com/v1/test/getcrumb
        # https://ups.analytics.yahoo.com/ups/58824/sync?format=json
        # https://geo.yahoo.com/p
        # https://finance.yahoo.com/
        # https://query1.finance.yahoo.com/v1/finance/trending/US?count=5&useQuotes=true&fields=logoUrl%2CregularMarketChangePercent%2CregularMarketPrice

        logging.info( f"%s - get() dummy session for cookie extraction" % cmi_debug )
        logging.info( f"%s - Using url: {self.dummy_url}" % cmi_debug )

        if type_of_get == 0:
            logging.info( f"%s - get() using simple HTML egine..." % cmi_debug )
            #with self.html_session.get(self.dummy_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.html_resp0:
            self.html_resp0 = requests.get(self.dummy_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 )
            print ( f"====================== {self.yti} / Dummy HTML session cookies / pre ============================" )
            for i in self.html_resp0.cookies.items():
                print ( f"{i}" )
                
            # Xray DEBUG
            print ( f"====================== {self.yti} / Dummy HTML session cookies / post ===========================" )
            for i in self.html_resp0.cookies.items():
                print ( f"{i}" )

            print ( f"================================================================================================\n" )
            print ( f">>> DEBUG: dump resp0 txt\n" )
            print ( f"{self.html_resp0.text}" )
            print ( f"=========================================== end ================================================\n" )
            return

        if type_of_get == 1:
            logging.info( f"%s - get() using JAVASCRIPT engine..." % cmi_debug )
            with self.js_sesion.get(self.dummy_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
                # Xray DEBUG
                print ( f"=============== {self.yti} / Dummy JAVASCRIPT session cookies ==================================" )
                for i in self.js_session.cookies.items():
                    print ( f"{i}" )

                print ( f"================================================================================================\n" )
                print ( f">>> DEBUG: dump JAVASCRIPT resp0 txt\n" )
                print ( f"{self.js_resp0.text}")
                print ( f"=========================================== end ================================================\n" )

                # self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack
                # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
                return
        return              # safety

#######################################################################
# method 4
    def update_cookies(self):
        # assumes that the requests session has already been established
        cmi_debug = __name__+"::"+self.update_cookies.__name__+".#"+str(self.yti)
        logging.info( f"%s - Swap in GOOD cookies from dummy session" % cmi_debug )
        
        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / update_cookies ======================================" )
            print ( f"js_resp0:" )
            for i in self.js_resp0.cookies.items():
                print ( f"{i}" )

            print ( f"js_session:" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )


        hot_cookies = requests.utils.dict_from_cookiejar(self.js_session.cookies)  
        print ( f">>> DEBUG: Hot cookie jar\n {json.dumps(hot_cookies)}" )
        print ( f"============================================= end ===========================================\n" )

        #self.js_session.cookies.update({'A1': self.js_resp0.cookies['A1']} )    # yahoo cookie hack
        #self.js_session.cookies.update({'A1': self.js_resp0.cookies['A1']} )    # yahoo cookie hack
        return

#######################################################################
# method 5
    def do_html_get(self):
        """
        get simple raw HTML data structure - processed by simple HTML engine
        NOTE: get URL is assumed to have allready been set (self.a_urlp)
              Assumes cookies have already been set up. NO cookie update done here
        """
        cmi_debug = __name__+"::"+self.do_html_get.__name__+".#"+str(self.yti)
        logging.info( f"%s - HTML request on URL: {self.a_urlp}" % cmi_debug )
        logging.info( f"%s - Simple HTML Request get() processing..." % cmi_debug )
        with self.html_session.get(self.a_urlp, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp1:
            logging.info('%s - HTML Request get() completed!- saved HTML dataset' % cmi_debug )
            self.yf_htmldata = self.js_resp1.text
            self.jorh = 0
            # On success, HTML response is saved in Class Global accessor -> self.js_resp0
            # TODO: should do some get() failure testing here

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )
            for i in self.html_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / HTML get() session cookies ================================\n" )

        return

#######################################################################
# method 6
    def do_js_get(self):
        """
        get JAVAScript  data structure - processeed by the JAVASCRIPT engine
        NOTE: get URL is assumed to have allready been set (self.a_urlp)
              Assumes cookies have already been set up. NO cookie update done here
        """
        cmi_debug = __name__+"::"+self.do_js_get.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info( f"%s - JAVASCRIPT request on URL: {self.a_urlp}" % cmi_debug )
        logging.info('%s - Javascript engine Request get() processing...' % cmi_debug )
        with self.js_session.get(self.a_urlp, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp2:
            # On success, native JAVASCRIPT response/page is saved in Class Global accessor -> self.js_resp2
            logging.info('%s - Javascript Request get() completed! - saved  JS dataset' % cmi_debug )
            self.js_rtemp = self.js_resp2           # take a copy of the JS response handle
            
            logging.info('%s - Javascript engine down rendering simple HTML page...' % cmi_debug )
            self.js_rtemp.html.render()             # render a raw HTML (non-JS) page & create response handle
            self.yf_jsdata = self.js_rtemp.text     # save down rendered HTML data page (built by JAVASCRIPT engine) - NOT the pure JAVASCRIPT page
            logging.info( "%s - Javascript down rendering completed! - saved HTML dataset" % cmi_debug )
            self.jorh = 1
                                                    # TODO: should do some render() failure testing here

        # TODO: should do some get() failure testing everywhere in here
        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / JS get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / JS get() session cookies ================================\n" )

        return
    
    def debug_monster(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the embedded webpage [Stock:Top Gainers] html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.debug_monster.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        r = requests.get("https://finance.yahoo.com/gainers" )
        logging.info( "%s - read html stream" % cmi_debug )

        self.soup = BeautifulSoup(r.text, 'html.parser')
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        #logging.info('%s - save data object handle' % cmi_debug )
        #self.tag_tbody = self.soup.find('tbody')
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})   # simpTblRow
        self.tr_rows = self.tag_tbody.find(attrs={"class": "simpTblRow"})

        print ( f">>> DEBUG: r-text\n" )
        print ( f" {r.text} " )

        logging.info('%s - close url handle' % cmi_debug )
        r.close()
        return


function reverse_word(string word)
    reversed = ""
    for letter in word:
            reversed = letter + reversed
    return reversed

function check_all_palindromes(array arr)
        reversed1 = reverse_word(word1)
        reversed2 = reverse_word(word2)
        reversed3 = reverse_word(word3)

        if arr[0] does not equal reversed1:
                return false

        if arr[1] does not equal reversed2:
                return false

        if arr[2] does not equal reversed3:
                return false
        return true