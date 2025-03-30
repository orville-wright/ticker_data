#!/home/orville/venv/devel/bin/python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import argparse

# logging setup
logging.basicConfig(level=logging.INFO)

from requests_html import HTMLSession

#####################################################

class y_cookiemonster:
    """Class to extract Top Gainer data set from finance.yahoo.com"""

    # global accessors
    tg_df0 = ""          # DataFrame - Full list of top gainers
    tg_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    tg_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    tl_dfo = ""
    tl_df1 = ""
    tl_df2 = ""

    all_tag_tr = ""      # BS4 handle of the <tr> extracted data
    yti = 0
    cycle = 0           # class thread loop counter

    yahoo_headers = { \
                            'authority': 'finance.yahoo.com', \
                            'path': '/screener/predefined/day_gainers/', \
                            'referer': 'https://finance.yahoo.com/screener/', \
                            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"', \
                            'sec-ch-ua-mobile': '"?0"', \
                            'sec-fetch-mode': 'navigate', \
                            'sec-fetch-user': '"?1', \
                            'sec-fetch-site': 'same-origin', \
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' }
        
##############################################################################
    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        # init empty DataFrame with present colum names
        self.tg_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.tg_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.yti = yti
        return

##############################################################################
# method #1
    def get_scap_data(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw sring data out of"""
        """the embedded webpage [Stock:Top Gainers] html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_scap_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        r = requests.get("https://finance.yahoo.com/gainers" )
        logging.info('%s - read html stream' % cmi_debug )
        self.soup = BeautifulSoup(r.text, 'html.parser')
        # ATTR style search. Results -> Dict
        # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
        logging.info('%s - save data object handle' % cmi_debug )
        self.tag_tbody = self.soup.find('tbody')
        self.all_tag_tr = self.soup.find_all(attrs={"class": "simpTblRow"})   # simpTblRow
        #self.tr_rows = self.tag_tbody.find(attrs={"class": "simpTblRow"})

        print ( f">>> DEBUG:\n {r.text}" )

        logging.info('%s - close url handle' % cmi_debug )
        r.close()
        return

###########################################################################################
# method #2
    def get_js_data(self, js_url):
        """Connect to finance.yahoo.com and open a Javascript Webpage"""
        """Process with Javascript engine and return JS webpage handle"""
        """Optionally the Javascript engine can render the webspage as Javascript and"""
        """and then hand back the processed JS webpage. - This is currently didabled"""

        cmi_debug = __name__+"::"+self.get_js_data.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        js_url = "https://" + js_url

        #test_url = "https://www.whatismybrowser.com/detect/is-javascript-enabled"
        #test_url = "https://www.javatester.org/javascript.html"
        #test_url = "https://finance.yahoo.com/screener/predefined/small_cap_gainers/"

        logging.info( f"%s - Javascript engine setup..." % cmi_debug )
        logging.info( f"%s - URL: {js_url}" % cmi_debug )
        logging.info( f"%s - Init JS_session HTMLsession() setup" % cmi_debug )

        js_session = HTMLSession()
        
        #js_resp0 = js_session.get( test_url )
        #js_resp0 = js_session.get( test_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as js_resp0:
        #with js_session.get( test_url, stream=True, headers=self.yahoo_headers, cookies=self.yahoo_headers, timeout=5 ) as js_resp0:
        # with js_session.get( 'https://www.javatester.org/javascript.html', stream=True, timeout=5 ) as self.js_resp0
        with js_session.get( js_url ) as self.js_resp0:
        
            logging.info( f"%s - JS_session.get() sucessful !" % cmi_debug )
        
        logging.info( f"%s - html.render()... diasbled" % cmi_debug )
        #self.js_resp0.html.render()
        # this needs to be a setting that can be controlled from the caller.
        # it correnlty times-out with pypuppeteer timeout failure

        # print ( f"{self.js_resp0.text}" )
        # logging.info( f"%s - html.render() DONE !" % cmi_debug )

        hot_cookies = requests.utils.dict_from_cookiejar(self.js_resp0.cookies)
        logging.info( f"%s - Swap in JS reps0 cookies into js_session yahoo_headers" % cmi_debug )
        js_session.cookies.update(self.yahoo_headers)
        #logging.info( f"%s - Dump JS cookie JAR\n {json.dumps(hot_cookies)}" % cmi_debug )

        # self.js_session.cookies.update({'bm_sv': self.js_resp0.cookies['bm_sv']} )    # NASDAQ cookie hack
        # self.js_session.cookies.update(self.nasdaq_headers)    # load cookie/header hack data set into session

        return self.js_resp0