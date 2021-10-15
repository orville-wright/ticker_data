#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading
import json

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class y_techevents:
    """
    Class to extract Simple Today/Short/Medium/Long term indicator data set from finance.yahoo.com
    """

    # global accessors
    te_sentiment = {}   # Dit contains a tuple of elements, e.g. (te_sml, te_timeframe, "Grey", "Sideways", "Neutral")
    te_resp0 = ""
    te_jsondata0 = ""
    te_zone = ""
    te_short = ""
    te_mid = ""
    te_long = ""
    te_srs_zone = ""
    te_all_url = ""
    yti = 0
    cycle = 0           # class thread loop counter

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f"{cmi_debug} - Instantiate.#{yti}" )
        # init empty DataFrame with present colum names
        self.yti = yti
        return


# method #1
    def form_api_endpoints(self, symbol):
        """
        For Technical event Indicators endpoint for the req get()
        This page is where the Free view into some technical idicators are show with full TEXT strings descriptions.
        NOTE: This is a teaser page. Tech Events are only available to paid-for subscrption users. But the teaser page shows
        a clutch of free indicators...So we'll take the free Tech Event indicators, for now.
        1. Today, Short, intermediate, Long Term technical analysis
        2. Support, Resistance, Stop loss levels
        """
        cmi_debug = __name__+"::"+self.form_api_endpoints.__name__+".#"+str(self.yti)
        logging.info( f"{cmi_debug} - form API endpoint URL(s)" )
        self.symbol = symbol.upper()
        self.te_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical="
        self.te_all_url = "https://finance.yahoo.com/quote/" + self.symbol + "?p=" + self.symbol
        self.te_short_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=short"
        self.te_mid_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=intermediate"
        self.te_long_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=long"
        #
        logging.info( f"================================ Tech Events API endpoints ================================" )
        logging.info( f"{cmi_debug} - API endpoint #0: [ {self.te_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #1: [ {self.te_all_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #1: [ {self.te_short_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #3: [ {self.te_mid_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #4: [ {self.te_long_url} ]" )
        return


# method #2
    def get_te_zones(self):
        """
        Connect to finance.yahoo.com and extract (scrape) the raw JSON data out of
        the embedded webpage [finance.yahoo.com/chart/GOL?technical=short] html data table.
        Sabe JSON to class global attribute: self.te_resp0.text
        """
        cmi_debug = __name__+"::"+self.get_te_zones.__name__+".#"+str(self.yti)
        logging.info( f"{cmi_debug} - IN" )
        with requests.get( self.te_all_url, stream=True, timeout=5 ) as self.te_resp0:
            logging.info( f"{cmi_debug} - get() data / storing..." )
            self.soup = BeautifulSoup(self.te_resp0.text, 'html.parser')
            logging.info( f"{cmi_debug} - Main data zone: {len(self.soup)} lines extracted / Done" )
        #
        self.te_zone = self.soup.find(attrs={"id": "chrt-evts-mod"} )
        self.te_lizones = self.te_zone.find_all('li')
        #self.te_today = self.te_zone.find(attrs={"class": "Fz(xs) Mb(4px)"} )
        self.te_today = self.te_zone.find(attrs={"class": "W(1/4)--mobp W(1/2) IbBox"} )
        self.te_today_pat = self.te_zone.find(attrs={"class": "Mb(4px) Whs(nw)"} )
        """
        print ( f"===============================================================" )
        print ( f">>>DEBUG<<< : te_today" )
        print ( f"{self.te_today}" )
        print ( f"===============================================================" )
        print ( f"{self.te_today.next_element}" )
        print ( f"===============================================================" )
        print ( f"{self.te_today.next_element.next_element}" )
        print ( f"===============================================================" )
        print ( f"{self.te_today.next_element.next_sibling}" )
        print ( f"===============================================================" )
        print ( f"{self.te_today_pat}" )
        print ( f"===============================================================" )
        """
        return


# method #3
    def build_te_data(self):
        """
        Build-out Perfromance Outlook Technical Events dict
        Dict structure: { key: (embeded 5 element tuple) }
        e.g. {0: (te_sml, te_timeframe, "Grey", "Sideways", "Neutral") }
        1.  tme_sml : (Short/Medium/Long)
        2.  tm_timeframe : Time frame that this Tech Event covers (days/weeks/months)
        3.  Tech Event Indicator: Red/Grey/Green   * not included in final dict
        4.  Tech Event Indicator: Down/Sideways/Up *  not included in final dict
        5.  Tech Event Indicator: Bearish/Neutral/Bullish
        """
        cmi_debug = __name__+"::"+self.build_te_data.__name__+".#"+str(self.yti)

        logging.info( f"{cmi_debug} - IN" )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info( f"{cmi_debug} - Scan quote Tech Event indicators" )
        te_today = self.te_today.next_element.next_element.string
        print ( f"Tech event pattern today: {te_today}" )
        y = 0
        for j in self.te_lizones:
            for i in j:
                te_strings = i.strings
                te_sml = next(te_strings)
                te_timeframe = next(te_strings)
                red = i.svg.parent.contents
                red_down = re.search('180deg', str(red) )
                grey_neutral = re.search('90deg', str(red) )
                if red_down:        # Red Bearish
                    self.te_sentiment.update({y: (te_sml, te_timeframe, "Bearish")} )
                    y += 1
                elif grey_neutral:  # Grey Neutral
                    self.te_sentiment.update({y: (te_sml, te_timeframe, "Neutral")} )
                    y += 1
                else:               # Green Bullish
                    self.te_sentiment.update({y: (te_sml, te_timeframe, "Bullish")} )
                    y += 1

        self.te_sentiment.update({y: ("Today", "1D", te_today)} )
        logging.info('%s - populated new Tech Event dict' % cmi_debug )
        return y        # number of rows inserted into Tech events dict
