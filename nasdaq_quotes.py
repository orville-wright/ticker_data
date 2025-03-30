#!/home/orville/venv/devel/bin/python3
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import logging
import argparse
import json

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class nquote:
    """Class to get live Market Data Quote from NASDAQ.com data source"""

    # global accessors
    yti = 0                 # Unique instance identifier
    cycle = 0               # class thread loop counter
    args = []               # class dict to hold global args being passed in from main() methods
    quote_json0 = ""        # JSON dataset #1 : dummy_session + Update_cookiues + do_simple_get
    quote_json1 = ""        # JSON dataset #1 quote summary
    quote_json2 = ""        # JSON dataset #2 quote watchlist
    quote_json3 = ""        # JSON dataset #3 quote premarket
    quote_json4 = ""        # JSON dataset #4 quote asset_class
    js_resp0 = ''           # session response handle for : dummy_session + Update_cookiues + do_simple_get
    js_resp1 = ''           # session response handle for : self.summary_url
    js_resp2 = ''           # session response handle for : self.watchlist_url
    js_resp3 = ''           # session response handle for : self.premarket_url
    js_resp4 = ''           # session response handle for : self.info_url
    path = ""
    info_url = ""
    quote_url = ""
    js_session = ""         # main requests session
    asset_class = ""        # global NULL TESTing indicator (important)
    summary_url = ""
    watchlist_url = ""
    premarket_url = ""

# #####################################################################################
# REFACTOR notes
# All of these methods has been removed from this class and refactored/migrated
# into ->  nasdaq_wrangler.py @ class::nq_wrangler
#
# def build_data(self): --> REFACTORED --> setup_zones
# nulls_summary --> REFACTORED --> z1_summary
# nulls_watchlist --> REFACTORED --> z2_watchlist
# nulls_premarket --> REFACTORED --> z3_premarket
# new method: pre_load_z2
# new method: pre_load_z3
# new method: pre_load_z1
# new method: clean_cast

#######################################################################################
#  NASDAQ.com header/cookie hack
    nasdaq_headers = { \
                    'authority': 'api.nasdaq.com', \
                    'path': '/api/quote/IBM/info?assetclass=stocks', \
                    'origin': 'https://www.nasdaq.com', \
                    'referer': 'https://www.nasdaq.com', \
                    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', \
                    'sec-ch-ua-mobile': '"?0"', \
                    'sec-fetch-mode': 'cors', \
                    'sec-fetch-site': 'same-site', \
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' }

######################################################################
# method 0
    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with preset colum names
        self.args = global_args                                # Only set once per INIT. all methods are set globally
        #self.quote_df0 = pd.DataFrame(columns=[ 'Symbol', 'Co_name', 'arrow_updown', 'Cur_price', 'Prc_change', 'Pct_change', 'Open_price', 'Prev_close', 'Vol', 'Mkt_cap', 'Exch_timestamp', 'Time' ] )
        self.yti = yti
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.nasdaq_headers)    # load DEFAULT cookie/header hack package into session
        return

######################################################################
# method 1
    def update_headers(self, symbol, asset_class):
        cmi_debug = __name__+"::"+self.update_headers.__name__+".#"+str(self.yti)
        logging.info( f"%s - CALLED" % cmi_debug )
        self.symbol = symbol.upper()
        path = "/api/quote/" + self.symbol + "/info?assetclass=" + asset_class
        logging.info( f"%s - Insert ticker symbol path into cookie..." % cmi_debug )
        self.js_session.cookies.update({'path': path} )
        logging.info( f"%s - cookies/headers :path: object set to: {path}" % cmi_debug )

        if self.args['bool_xray'] is True:
            print ( f"========================= {self.yti} / Updated session headers ============================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================================= end =============================================\n" )
            
        return

######################################################################
# method 2
    def update_cookies(self):
        # assumes that the requests session has already been established
        cmi_debug = __name__+"::"+self.update_cookies.__name__+".#"+str(self.yti)
        logging.info('%s - REDO the cookie extract & update  ' % cmi_debug )
        self.js_session.cookies.update({'ak_bmsc': self.js_resp0.cookies['ak_bmsc']} )    # NASDAQ cookie hack
        return

######################################################################
# method 3
    def form_api_endpoint(self, symbol, asset_class):
        """
        This is the quote endpoints for the req get()
        As of 1 Oct, 2021...
        - Nasdaq has a new data model that splits quote data across 4 key API endpoints. Of which,  2 are very intersting.
        """
        cmi_debug = __name__+"::"+self.form_api_endpoint.__name__+".#"+str(self.yti)
        logging.info('%s - form API endpoint URL' % cmi_debug )
        self.symbol = symbol.upper()
        self.quote_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/info?assetclass=" + asset_class
        self.info_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/info?assetclass=" + asset_class
        self.summary_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/summary?assetclass=" + asset_class
        self.premarket_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/extended-trading?assetclass=" + asset_class + "&markettype=pre"
        #
        self.watchlist_url = "https://api.nasdaq.com/api/quote/watchlist?symbol=" + self.symbol + "%7c" + asset_class
        wurl_log1 = "https://api.nasdaq.com/api/quote/watchlist?symbol=" + self.symbol    # hack f-strings doesnt like "%" inside {}
        wurl_log2 = f"7c{asset_class}"         # hack f-strings doesnt like "%" inside {}
        #
        logging.info( f"================================ Quote API endpoints ================================" )
        logging.info( f"%s - API #0: [ {self.quote_url} ]" % cmi_debug )
        logging.info( f"%s - API #1: [ {self.summary_url} ]" % cmi_debug )
        logging.info( f"%s - API #2: [ {wurl_log1}%%{wurl_log2} ]" % cmi_debug )
        logging.info( f"%s - API #3: [ {self.premarket_url} ]" % cmi_debug )
        logging.info( f"%s - API #4: [ {self.info_url} ]" % cmi_debug )
        self.quote_url = self.quote_url
        return

######################################################################
# method 4
    def do_simple_get(self):
        """
        A basic connection/cookie/headers setup method
        INFO: we simply ping www.nasdaq.com. No need for an API specific url. That comes later.
        Assumes the cookies have already been set up
        NO cookie update done!!!
        """
        cmi_debug = __name__+"::"+self.init_blind_session.__name__+".#"+str(self.yti)
        logging.info('%s - Blind request get() on base url' % cmi_debug )
        with self.js_session.get('https://www.nasdaq.com', stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
            logging.info('%s - Request get() done' % cmi_debug )
            # DEBUG : Xray
            if self.args['bool_xray'] is True:
                print ( f"=========== do_simple_get.{self.yti} do_simple_get cookies  ===================" )
                for i in self.js_session.cookies.items():
                    print ( f"{i}" )
                print ( f"===================== do_simple_get.{self.yti} end  ===========================" )

        # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

######################################################################
# method 5
    def init_dummy_session(self):
        """
        a cookie setup method
        note: we ping www.nasdaq.com. No need for a API specific url, as this should be the FIRST get
        Our goal is simply find & extract secret cookies. Nothing more.
        """
        cmi_debug = __name__+"::"+self.init_dummy_session.__name__+".#"+str(self.yti)
        with self.js_session.get('https://www.nasdaq.com', stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp0:
            logging.info( f"%s - extract cookies  " % cmi_debug )

            # DEBUG : Xray
            if self.args['bool_xray'] is True:
                print ( f"===================== dummy_session.{self.yti} cookies  ===========================" )
                for i in self.js_session.cookies.items():
                    print ( f"{i}" )
                print ( f"========================== dummy_session.{self.yti} end  ===========================" )

            logging.info( f"%s - update GOOD warm cookie  " % cmi_debug )

        # if the get() succeds, the response handle is automatically saved in Class Global accessor -> self.js_resp0
        return

######################################################################
# method 6
    def learn_aclass(self, symbol):
        """
        return : the asset identifier (stocks or etf)
        """
        cmi_debug = __name__+"::"+self.learn_aclass.__name__+".#"+str(self.yti)
        logging.info( f"%s - Learn asset class @ API: {self.info_url}" % cmi_debug )
        with self.js_session.get(self.info_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp1:
            logging.info( f"%s - Extract default guess data..." % cmi_debug )
            self.quote_json1 = json.loads(self.js_resp1.text)
            #figure out asset_class which defines which API endpoint to use...
            self.asset_class = -1
            t_info_url = "https://api.nasdaq.com/api/quote/" + self.symbol + "/info?assetclass="
            for i in ['stocks', 'etf']:
                test_info_url = t_info_url + i
                with self.js_session.get(test_info_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp4:
                    logging.info( f'%s - Test {symbol} asset_class [ {i} ] @ API: {test_info_url}' % cmi_debug )
                    self.quote_json4 = json.loads(self.js_resp4.text)
                    if self.quote_json4['status']['rCode'] == 200:
                        self.asset_class = i
                        logging.info( f'%s - Asset_class is: [ {i} ] !' % cmi_debug )
                        break
                    else:
                        logging.info( f'%s - Asset_class is NOT: [ {i} ] !' % cmi_debug )
                        test_info_url = ""

        logging.info( f"%s - Done" % cmi_debug )
        return i    # asset_class identifier  (stocks or etf)

######################################################################
# method 7
    def get_nquote(self, symbol):
        """
        Access NEW nasdaq.com JAVASCRIPT page [.../api//quote/]
        Extract the native JSON dataset. Page is a pure JSON datset struct, so no BS4 scraping needed.
        NOTE: Javascript engine process is NOT required as the output page is simple JSON text
        NOTE: API URL get will = success for any URL endpoint, includes non-existent symbols & symbols !
              that return bad/NULL data set (i.e. ETF's, which are not company's or regular symbols)
        NOTE: Nasdaq changed quote data model. Data is now split across mutliple API endpoints
        """
        cmi_debug = __name__+"::"+self.get_nquote.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.qs = symbol

        with self.js_session.get(self.summary_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp1:
            logging.info( f"%s - Stage #1 / Summary / get() data / storing..." % cmi_debug )
            logging.info( f"%s - API: {self.summary_url}" % cmi_debug )
            self.quote_json1 = json.loads(self.js_resp1.text)
            logging.info( f"%s - Stage #1 - Done" % cmi_debug )

        with self.js_session.get(self.watchlist_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp2:
            logging.info( f"%s - Stage #2 / Watchlist / get() data / storing..." % cmi_debug )
            # cant do logging.info on self.watchlist_url b/c it has '%7c' in url as a specla seperator for nasdaq.com API
            self.quote_json2 = json.loads(self.js_resp2.text)
            logging.info( f"%s - Stage #2 - Done" % cmi_debug )

        with self.js_session.get(self.premarket_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp3:
            logging.info( f"%s - Stage #3 / premarket / get() data / storing..." % cmi_debug )
            logging.info( f"%s - API: {self.premarket_url}" % cmi_debug )
            self.quote_json3 = json.loads(self.js_resp3.text)
            logging.info( f"%s - Stage #3 - Done" % cmi_debug )

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"===================== get_nquote.{self.yti} session cookies : {self.qs} ===========================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"===================== get_nquote.{self.yti} session cookies : {self.qs} ===========================" )
        return

#######################################################################
# method 7
    def get_js_nquote(self, symbol):
        """
        Access NEW nasdaq.com JAVASCRIPT page [unusual volume] and extract the native JSON dataset
        JSON dataset contains *BOTH* UP vol & DOWN vol for top 25 symbols, right now!
        NO BeautifulSOup scraping needed anymore. We access the pure JSON datset via native API rest call
        NOTE: Javascript engine is required, Cant process/read a JS page via requests(). The get() hangs forever
        NOTE: Javascript currently disbaled, since we access he data directly via API endpoint
        """
        cmi_debug = __name__+"::"+self.get_js_nquote.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        self.symbol = symbol
        with self.js_session.get(self.quote_url, stream=True, headers=self.nasdaq_headers, cookies=self.nasdaq_headers, timeout=5 ) as self.js_resp1:
            # read the webpage with our Javascript engine processor
            logging.info('%s - Javascript engine processing...' % cmi_debug )
            self.js_resp1.html.render()    # this isn't needed for this URL becuase is a RAW JSON output page. NOT Javascript
            logging.info('%s - Javascript engine completed!' % cmi_debug )
            logging.info('%s - summary json quote data package extracted / storing...' % cmi_debug )
            self.quote_json1 = json.loads(self.js_resp1.text)

        # Xray DEBUG
        if self.args['bool_xray'] is True:
            print ( f"========================== {self.yti} - get_js_nquote::session cookies ================================" )
            for i in self.js_session.cookies.items():
                print ( f"{i}" )
            print ( f"========================== {self.yti} - get_js_nquote::session cookies ================================" )
        return