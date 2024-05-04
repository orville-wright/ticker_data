!/usr/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, date
import hashlib
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
    cycle = 0               # class thread loop counter
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods
    a_urlp = ""             # a url
    path = ""               # the path component of our url : /screener/predefined/small_cap_gainers/
    yf_htmldata = ""        # live HTML data text from a sucecssful html get()
    yf_jsdata = ""          # live JAVASCRIPT page data - NOT the HTML down rendered page
    js_resp0 = ""           # dummy html get() - response handle from a simple HTML get() - no JAVASCRIPT engine
    js_resp1 = ""           # HTML engine - response handle from a real live HTML get()
    js_resp2= ""            # JAVASCRIPT engine - response handle from a real live Javascript get()
                            # header struct
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

#######################################################################
# init
    def __init__(self, yti, path, global_args):
        self.yti = yti
        cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(self.yti)
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args
        self.path = path
        self.cycle = 1
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.yahoo_headers)     # load cookie/header hack data set into session
        self.a_urlp = urlparse('https://www.dummyurl.com')
        return
    
#######################################################################
# method 1
    def form_url_endpoint(self):
        """
        NOTE: assumes that path header/cookie has been set first
        URL endpoints available (examples)
        https://finance.yahoo.com/screener/predefined/small_cap_gainers/
        https://finance.yahoo.com/quote/IBM/?p=IBM
        https://finance.yahoo.com/quote/IBM/news?p=IBM
        https://finance.yahoo.com/quote/IBM/press-releases?p=IBM
        https://finance.yahoo.com/quote/IBM/reports?p=IBM
        """

        cmi_debug = __name__+"::"+self.form_url_endpoint.__name__+".#"+str(self.yti)
        logging.info( f"%s - form URL endpoint for: {symbol}" % cmi_debug )
        self.a_urlp = 'https://finance.yahoo.com' + self.path    # use global accessor (so all paths are consistent)
        logging.info( f"%s - API endpoint URL: {self.a_urlp}" % cmi_debug )
        return

#######################################################################
# method 2
    def update_headers(self):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        logging.info( f"%s - inser cookie/header :path: object..." % cmi_debug )
        self.js_session.cookies.update({'path': self.path} )
        logging.info( f"%s - :path: cookie - [ {self.path} ]" % cmi_debug )

        if self.args['bool_xray'] is True:
            print ( f"=========================== {self.yti} / session cookies ===========================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )

        return

#######################################################################
# method 3
    def init_dummy_session(self):
        cmi_debug = __name__+"::"+self.init_dummy_session.__name__+".#"+str(self.yti)
        """
        NOTE: we ping finance.yahoo.com
              No API specific url needed. 1st get  does need it. - Goal is to find & extract secret cookies
        Overwrites js_resp0 - initial session handle, *NOT* the main data session handle (js_resp2)
        """

        with self.js_session.get('https://www.finance.yahoo.com', stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - extract & update GOOD cookie  ' % cmi_debug )
            # self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack
            # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

#######################################################################
# method 4
    def update_cookies(self):
        # assumes that the requests session has already been established
        cmi_debug = __name__+"::"+self.update_cookies.__name__+".#"+str(self.yti)
        logging.info('%s - REDO the cookie extract & update  ' % cmi_debug )
        self.js_session.cookies.update({'B': self.js_resp0.cookies['B']} )    # yahoo cookie hack
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
        with self.js_session.get(self.a_urlp, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as self.js_resp1:
            logging.info('%s - HTML Request get() completed!- saved HTML dataset' % cmi_debug )
            self.yf_htmldata = self.js_resp1.text
            # On success, HTML response is saved in Class Global accessor -> self.js_resp0
            # TODO: should do some get() failure testing here

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / HTML get() session cookies ================================" )

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
            logging.info('%s - Javascript down rendering completed! - saved HTML dataset' % cmi_debug )
                                                    # TODO: should do some render() failure testing here

        # TODO: should do some get() failure testing everywhere in here
        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} / JS get() session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} / JS get() session cookies ================================" )

        return
    
