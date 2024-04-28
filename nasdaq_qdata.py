#!/usr/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading
import json

from bigcharts_md import bc_quote

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class qd_nquote:
    """Class to get live Market Data Quote from NASDAQ.com data source"""

    # global accessors
    qd_quote = {}              # quote as dict
    qd_quote_json0 = ""        # JSON dataset #1 : dummy_session + Update_cookiues + do_simple_get
    qd_quote_json1 = ""        # JSON dataset #1 quote summary
    qd_quote_json2 = ""        # JSON dataset #2 quote watchlist
    qd_quote_json3 = ""        # JSON dataset #3 quote premarket
    qd_quote_json4 = ""        # JSON dataset #4 quote asset_class
    qd_data0 = []              # JSON data payload
    yti = 0                    # Unique instance identifier
    qd_cycle = 0               # class thread loop counter
    args = []                  # class dict to hold global args being passed in from main() methods
    qd_js_session = ""         # main requests session
    quote_url = ""
    summary_url = ""
    watchlist_url = ""
    premarket_url = ""
    info_url = ""
    path = ""
    asset_class = ""        # global NULL TESTing indicator (important)

                            # NASDAQ.com header/cookie hack
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

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        self.args = global_args                                # Only set once per INIT. all methods are set globally
        self.yti = yti
        self.js_session = HTMLSession()                        # init JAVAScript processor early
        self.js_session.cookies.update(self.nasdaq_headers)    # load DEFAULT cookie/header hack package into session
        return

# ###################################################################################################################################
# method 1
    def qd_build_data(self, yti, qd_1, qd_2, qd_3):
        """
        Build-out the full quote data structure thats tidy & clean. All fields sourced from the extracted JSON dataset.
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.build_data.__name__+".#"+str(self.yti)
        logging.info('%s - build quote data payload from JSON' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - prepare jsondata accessors [11/20/30]...' % cmi_debug )
        self.jsondata11 = qd_1                              # summary
        self.jsondata20 = qd_2                              # watchlist
        self.jsondata30 = qd_3                              # premarket

        #self.jsondata11 = self.quote_json1['data']                              # summary
        #self.jsondata20 = self.quote_json2['data'][0]                           # watchlist
        #self.jsondata30 = self.quote_json3['data']                              # premarket

    # Helper methods ##########################################################################################################
    """
    Private helper methods to poll nasdaq data model and test sanity for bad NULL data & bad/missing json keys
    NOTE: Keys & NULLs are somethimes bad becasue when the amrket is closed (e.g. premarket data). In that scenario
            this isn't an error scenario... but it's difficult logic to account for.
    Call before trying to access asdaq API json list indexes, as bad data will exert many hard errors.
    INFO: Checks 3 data zones in the nasdaq.com API json data model
            1. summary       :    self.jsondata11 = self.quote_json1['data']
            2. watchlist     :    self.jsondata20 = self.quote_json2['data'][0]
            3. pre-market    :    self.jsondata30 = self.quote_json3['data']
    """

    # ZONE #1 Summary zone....##############################################
    def z1_summary(self):
        """
        Process Zone 1 - Summary Zone
        """
        cmi_debug = __name__+"::"+nulls_summary.__name__+".#"+str(self.yti)
        logging.info( f'%s - probing json keys/fields for NULLs...' % cmi_debug )
        z = 1
        jd10_null_errors = 0
        jd_10s = ("PreviousClose", "MarketCap", "TodayHighLow", "AverageVolume", "OneYrTarget", "Beta", "FiftTwoWeekHighLow" )
        jd_10e = ("PreviousClose", "MarketCap", "TodayHighLow", "FiftyDayAvgDailyVol", "Beta", "FiftTwoWeekHighLow" )

        if self.asset_class == "stocks": jd_10 = jd_10s
        if self.asset_class == "etf": jd_10 = jd_10e

        try:
            y = self.jsondata11['summaryData']      # summary
        except TypeError:
            logging.info( f"%s - Probe #1.1 (API=summary): NULL data @: [data][summaryData]" % cmi_debug )
            jd10_null_errors = 1 + len(jd_10)       # everything in data set is BAD
            return jd10_null_errors
        except KeyError:
            logging.info( f"%s - Probe #1.2 (API=summary): NULL key @: [data][summaryData]" % cmi_debug )
            jd10_null_errors = 1 + len(jd_10)       # everything in data set is BAD
            return jd10_null_errors
        else:
            x = self.jsondata11['summaryData']
            for i in jd_10:
                print ( f"DEBUG: i: {i} " )
                try:
                    y = x[i]
                except TypeError:
                    logging.info( f"%s - Probe #1.3 (API=summary): NULL data @: [{i}] - RESET to: 0" % cmi_debug )
                    x[i]['value'] = 0      # fix the bad data by writing this field as 0
                    jd10_null_errors += 1
                except KeyError:
                    logging.info( f"%s - Probe #1.4 (API=summary): NULL key @: [{i}] - RESET to: 0" % cmi_debug )
                    x[i]['value'] = 0      # fix the bad data by writing this field as 0
                    jd10_null_errors += 1
                else:
                    z += 1
        logging.info( f"%s - End NULL probe #1 (API=summary) / errors: {jd10_null_errors} / 7" % cmi_debug )
        return jd10_null_errors


    # ZONE #2 watchlist zone....############################################
    def Z2_watchlist(self):
        """
        Process Zone 2
        This data zone is far more tollerant. keys/fields pre-exist. So this zone cant test for a
        non-existent/bad ticker symbol (or ETF/Fund). but this means errors are less severe.
        """
        cmi_debug = __name__+"::"+nulls_watchlist.__name__+".#"+str(self.yti)
        logging.info( f'%s - probing json keys/fields for NULLs...' % cmi_debug )
        z = 1
        x = self.jsondata20     # watchlist
        jd_20 = ("symbol", "companyName", "lastSalePrice", "netChange", "percentageChange", "deltaIndicator", "lastTradeTimestampDateTime", "volume" )
        jd20_null_errors = 0

        for i in jd_20:
            try:
                y = x[i]
            except TypeError:
                logging.info( f"%s - Probe #2.1 (API=watchlist): NULL data @: [{i}]" % cmi_debug )
                jd20_null_errors += 1
            except KeyError:
                logging.info( f"%s - Probe #2.2 (API=watchlist): NULL KEY data @: [{i}]" % cmi_debug )
                jd20_null_errors += 1
            else:
                z += 1
        logging.info( f"%s - End NULL probe #2 (API=watchlist) / errors: {jd20_null_errors} / 8" % cmi_debug )
        return jd20_null_errors

    # ZONE #3 premarket zone....########################################
    def Z3_premarket(self):
        """
        Process Zone 2 - Premarket Zone
        """
        cmi_debug = __name__+"::"+nulls_premarket.__name__+".#"+str(self.yti)
        logging.info( f'%s - probing json keys/fields for NULLs...' % cmi_debug )
        jd_31 = ("consolidated", "volume", "delta" )
        jd_30 = ("infoTable", "infoTable']['rows", "infoTable']['rows'][0", "infoTable']['rows'][0]['consolidated'",
                    "infoTable']['rows'][0]['volume'", "'infoTable']['rows'][0]['delta'" )
        z = 1
        jd31_null_errors = 0
        try:
            y = self.jsondata30['infoTable']['rows'][0]     # premarket
        except TypeError:
            logging.info( f"%s - Probe #3.1 (API=premarket): NULL data @: [infoTable][rows][0]" % cmi_debug )
            jd31_null_errors = 1 + len(jd_30)               # everything in data set is BAD
            return jd31_null_errors
        except KeyError:
            logging.info( f"%s - Probe #3.2 (API=premarket): NULL key @: [infoTable][rows][0]" % cmi_debug )
            jd31_null_errors = 1 + len(jd_30)               # everything in data set is BAD
            return jd31_null_errors
        else:
            x = self.jsondata30['infoTable']['rows'][0]
            for i in jd_31:
                try:
                    y = x[i]
                except TypeError:
                    logging.info( f"%s - Probe #3.3 (API=premarket): NULL data @: [{i}]" % cmi_debug )
                    jd31_null_errors += 1
                except KeyError:
                    logging.info( f"%s - Probe #3.4 (API=premarket): NULL key @: [{i}]" % cmi_debug )
                    jd31_null_errors += 1
                else:
                    z += 1
        logging.info( f"%s - End NULL probe 3 (API=premarket): errors: {jd31_null_errors} / 6" % cmi_debug )
        return jd31_null_errors

################################################################################################
# Quote DATA extractor ########################################################################
################################################################################################
    def qd_wrangle(self):
        """
        Do a lot of work cleaning the data.
        Main flow of wrangeling & cleaning is controlled from here. All other data wrangeling
        methods are called from here. 
        """
        wrangle_errors = 0
        null_count = 0
        a = self.z1_summary()                   # self.jsondata11 = self.quote_json1['data']
        b = self.z2__watchlist()                # self.jsondata20 = self.quote_json2['data'][0]
        c = self.z3_premarket()                 # self.jsondata30 = self.quote_json3['data']

        if a > 0:                       # Zone 1 (Data in Summary is in an Abberant state)
            logging.info( f'%s - Summary Zone 1 has ERRORS: [ {a} ]' % cmi_debug )
            a = self.nulls_summary()    # re-run it again just to see. a should come back as == 0
            if a > 0:                   # still BAD after 2nd attempt
                logging.info( f"%s - Nasdaq quote data is ABERRANT [ Zone 1:{a} zone 2:{b} zone 3:{c} ]" % cmi_debug )
                logging.info( f'%s - Abandon Nasdaq quote - Data is BAD' % cmi_debug )
                return wrangle_errors

            else:
                logging.info( f"%s - Repaired ABERRANT data [ Zone 1:{a} zone 2:{b} zone 3:{c} ]" % cmi_debug )
                wrangle_errors += 5     # Dataset allready started out life in bad shape
                # setup main JSON data zone accessors...
                # SUMMARY quote data seem OK to pre-process for loading
                wrangle_errors = self.qd_pre_load_z2()      # Watchlist
                wrangle_errors += self.qd_pre_load_z3()     # Pre-market
                wrangle_errors += self.qd_pre_load_z1()     # summary
                return wrangle_errors

        else:
            logging.info( f"%s - Good NOMINAL starting data [ Zone 1:{a} zone 2:{b} zone 3:{c} ]" % cmi_debug )
            wrangle_errors += 5     # Dataset allready started out life in bad shape
            wrangle_errors = self.qd_pre_load_z2()      # Watchlist
            wrangle_errors += self.qd_pre_load_z3()     # Pre-market
            wrangle_errors += self.qd_pre_load_z1()     # summary
            return wrangle_errors
            wrangle_errors += 50
            # a = z1_summary()   : zone 1
            # b = z2_watchlist() : zone 2
            # c = z3_premarket() : zone 3
        return wrangle_errors

#######################################################################################
# Zone 2
# WATCHLIST quote data
    def qd_pre_load_z2(self):
        """
        Zone 2 Watchlist pre-processor
        Fianlly extract Set all data field sfrom JSON and preload into variables
        for constructing into a List to eventually be written into a DataFrame
        """
        if self.quote_json2['data'] is not None:                                # bad payload? - can also test b == 0
            logging.info('%s - Zone #2 / Accessing data fields...' % cmi_debug )
            jsondata20 = self.quote_json2['data'][0]                            # HEAD of data payload
            co_sym = jsondata20['symbol']                                       # "IBM"
            co_name = jsondata20['companyName']                                 # "International Business Machines Corporation Common Stock"
            price = jsondata20['lastSalePrice']                                 # "$143.32"
            price_net = jsondata20['netChange']                                 # "+4.39"
            price_pct = jsondata20['percentageChange']                          # "3.16%"
            arrow_updown = jsondata20['deltaIndicator']                         # "up"
            price_timestamp = jsondata20['lastTradeTimestampDateTime']          # "2021-10-01T00:00:00"
            vol_abs = jsondata20['volume']                                      # "6,604,064"
            logging.info( '%s - Zone #2 /[8] fields - Done' % cmi_debug )
        else:
            logging.info('%s - Zone #2 / NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            wrangle_errors += -1

        return wrangle_errors

#######################################################################################
# Zone 3
# PRE-MARKET quote data - 2 data zones
    def qd_pre_load_z3(self):
        """
        Zone 3 Premarket pre-processor
        Fianlly extract Set all data field sfrom JSON and preload into variables
        for constructing into a List to eventually be written into a DataFrame
        """
        if self.quote_json3['data'] is not None:                                # bad payload? - can also test c == 0
            logging.info('%s - Zone #3 / Accessing data fields...' % cmi_debug )
            jsondata30 = self.quote_json3['data']                               # HEAD of data payload 0
            try:
                jsondata31 = self.quote_json3['data']['infoTable']['rows'][0]       # HEAD of data payload 1
            except TypeError:
                logging.info('%s - WARNING / infoTable payload is NULL' % cmi_debug )        # bad symbol json payload
                open_price = "$0.0 0.0 0.0"
                open_volume = 0                                  # e.g. "71,506"
                open_updown = "N/A"                              # e.g. "up"
                wrangle_errors += -1
            else:
                open_price = jsondata31['consolidated']                             # WARN: open_price info = multi-field string needs splitting e.g. "$140.8 +1.87 (+1.35%)"
                open_volume = jsondata31['volume']                                  # e.g. "71,506"
                open_updown = jsondata31['delta']                                   # e.g. "up"
                logging.info( '%s - Zone #3 / [3] fields - Done' % cmi_debug )
        else:
            logging.info('%s - Zonee #3 / zone [data] NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            wrangle_errors += -1
        
        return wrangle_errors

###############################################################################################3
# Zone 1
# Summary ZOne
    def qd_pre_load_z1(self):
        """
        Zone 1 Summary pre-processor
        Finally extract Set all data field sfrom JSON and preload into variables
        for constructing into a List to eventually be written into a DataFrame
        WARNING : This data zone is highly fragile and very intollerant. It constantly
                  contains lots of errors, missing fiels, bad fields etc. 
                  This is why we process it last !!!
        """

        if self.quote_json1['data'] is not None:                                # bad payload? - can also test a == 0
            logging.info('%s - Zone #1 / Accessing data fields...' % cmi_debug )
            fields_set = 0
            jsondata10 = self.quote_json1['data']['summaryData']                # HEAD of data payload
            prev_close = jsondata10['PreviousClose']['value']                   # e,g, "$138.93"
            fields_set += 1
            mkt_cap = jsondata10['MarketCap']['value']                          # e.g. "128,460,592,862"
            fields_set += 1
            today_hilo = jsondata10['TodayHighLow']['value']                    # WARN: multi-field string needs splitting/wrangeling e.g. "$143.97/$140.37"
            fields_set += 1

            if self.asset_class == "stocks":
                avg_vol = jsondata10['AverageVolume']['value']                      # e.g. "4,811,121" or N/A
                fields_set += 1
                oneyear_target = jsondata10['OneYrTarget']['value']                 # e.g. "$151.00"
                fields_set += 1
            else:
                pass

            logging.info( '%s - Zone #1 : {fields_set}/7 fields - Done' % cmi_debug )
        else:
            logging.info('%s - Zone #1 / NULL json payload - NOT regular stock' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            wrangle_errors += -1

        return wrangle_errors


########################################################################################
# wrangle, clean, cast & prepare the data ##############################################
    def clean_cast(self):
        """
        This method is a full LINEAR run down all known data elements
        Just try and process the data as fast as possible
        All variavble are loaded in support of creating a Qoute DataFram
        At the end just return a count of how many wrangle Errors we encountered
        """
        logging.info('%s - Begin heavy data wrangle workloads...' % cmi_debug )

        # >>> DEBUG Xray <<<
        if self.args['bool_xray'] is True:
            print ( f"\n================= Nasdaq quote data : raw uncleansed =================" )
            work_on = ['co_sym', 'co_name', 'price', 'price_net', 'price_pct', 'arrow_updown', \
                    'price_timestamp', 'vol_abs', 'open_price', 'open_volume', 'open_updown', \
                    'prev_close', 'mkt_cap', 'today_hilo', 'avg_vol', 'oneyear_target', 'beta', \
                    'LII_week_hilo']
            xx = iter(work_on)
            for name in work_on:
                print ( f"{next(xx)} / {eval(name)}" )
        # >>> DEBUG Xray <<<

        #################################### Begin Deep clean ##########################################
        co_sym_lj = co_sym.strip()
        #co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )          # left justify TXT & convert to raw string
        co_name_lj = (re.sub('[\'\"]', '', co_name) )                    # remove " ' and strip leading/trailing spaces
        co_name_lj = np.array2string(np.char.ljust(co_name_lj, 25) )     # left justify & convert to raw string
        co_name_lj = (re.sub('[\']', '', co_name_lj) )                   # remove " ' and strip leading/trailing spaces

        if price == "N/A":
            price_cl = 0
            logging.info('%s - Price is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        else:
            price_cl = (re.sub('[ $,]', '', price))                      # remove $ sign

        if price_net == "N/A":
            price_net_cl = 0
            logging.info('%s - Price NET is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        elif price_net == 'UNCH':
            price_net_cl = "Unch"
            logging.info('%s - Price NET is unchanged' % cmi_debug )
            wrangle_errors += 1
        else:
            price_net_cl = (re.sub('[\-+]', '', price_net))              # remove - + signs
            price_net_cl = float(price_net)

        if price_pct == "N/A":
            price_pct_cl = 0
            logging.info('%s - Price pct is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        elif price_pct == "UNCH":
            price_pct_cl = "Unch"
            logging.info('%s - Price pct is unchanged' % cmi_debug )
            wrangle_errors += 1
        elif price_pct == '':
            price_pct_cl = "No data"
            logging.info('%s - Price pct is bad, field is Null/empty' % cmi_debug )
            wrangle_errors += 1
        else:
            price_pct = (re.sub('[\-+%]', '', price_pct))                # remove - + % signs
            price_pct_cl = float(price_pct)

        # ################# open price(s) need extra treatment & care...
        """
        Open_price data elements are 3 fields concatinted into 1 long string / e.g. $140.8 +1.87 (+1.35%)
        This is a bad nasdaq strategy. We must split & post-process/wrangle the split fields
        """
        if open_price == "N/A" or open_price is None:
                """ Stage #0 """
                logging.info( f'%s - BAD open_price compound data: {type(open_price)} / {open_price} / set all to 0.0' % cmi_debug )
                open_price_cl = float(0)
                open_price_net = float(0)
                open_price_pct_cl = float(0)
                wrangle_errors += 3
        else:       # data is good...access 3 indices of sub-data from split list[]
            ops = open_price.split()
            logging.info( f"%s - Split open_price into {len(ops)} fields" % cmi_debug )

            """ Stage #1 """
            try:
                open_price = ops[0]                     # e.g. 140.8
            except IndexError:
                logging.info( f'%s - Bad key open_price: {type(open_price)} / setting to $0.0 / {open_price}' % cmi_debug )
                open_price = float(0)
                wrangle_errors += 1
            except ValueError:
                logging.info( f'%s - Bad open_price: {type(open_price)} / setting to $0.0 / {open_price}' % cmi_debug )
                open_price = float(0)
                wrangle_errors += 1
            else:
                open_price_cl = (re.sub('[ $,]', '', ops[0]))   # remove " " $ ,
                open_price_cl = float(open_price_cl)
                """ Stage #2 """

            if len(ops) != 1:   # the split failed to seperate all 3 elements. i.e. open_price_net & open_price_pct don't exist
                try:    # data is good...keep processing...
                    open_price_net = ops[1]                 # (test for missing data) - good data =  +1.87
                except IndexError:
                    logging.info( f'%s - Bad key open_price_net: {type(open_price_net)} / setting to $0.0 / {open_price_net}' % cmi_debug )
                    open_price_net = float(0)               # set NULL data to ZERO
                    wrangle_errors += 1
                except ValueError:
                    logging.info( f'%s - Bad open_price_net: {type(open_price_net)} / setting to $0.0 / {open_price_net}' % cmi_debug )
                    open_price_net = float(0)               # set NULL data to ZERO
                    wrangle_errors += 1
                except TypeError:
                    logging.info( f'%s - Bad open_price_net: {type(open_price_net)} / setting to $0.0 / {open_price_net}' % cmi_debug )
                    open_price_net = float(0)               # set NULL data to ZERO
                    wrangle_errors += 1
                else:
                    pass    # data is good...keep processing...
                    # INFO: no need of clean open_price_net - VAR is currently not used n our data model
                    """ Stage #3 """
                    try:
                        open_price_pct = ops[2]                 # (test for missing data) - good data = e.g. (+1.35%)"
                    except IndexError:
                        logging.info( f'%s - Bad key open_price_pct: {type(open_price_pct)} / setting to $0.0 / {open_price_pct}' % cmi_debug )
                        open_price_pct = float(0)               # set NULL data to ZERO
                        wrangle_errors += 1
                    except ValueError:
                        logging.info( f'%s - Bad open_price_pct: {type(open_price_pct)} / setting to $0.0 / {open_price_pct}' % cmi_debug )
                        open_price_pct = float(0)               # set NULL data to ZERO
                        wrangle_errors += 1
                    else:
                        open_price_pct_cl = (re.sub('[)(%]', '', price_pct))        # # remove " ", %  (leave +/- indicator)
                        # INFO: no need of clean open_price_net - VAR is currently not used n our data model
                        logging.info( f"%s - All 3 open_price vars sucessfully split & processed" % cmi_debug )
            else:
                open_price_net = float(0)
                open_price_pct_cl = float(0)

        #################################################
        if prev_close == "N/A":
            prev_close_cl = 0
            logging.info('%s - Prev close is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        else:
            prev_close_cl = (re.sub('[ $,]', '', prev_close))   # remove $ sign

        if mkt_cap == "N/A":
            mkt_cap_cl = float(0)
            logging.info('%s - Mkt cap is bad, found N/A data' % cmi_debug )
            wrangle_errors += 1
        elif mkt_cap == 0:
            mkt_cap_cl = float(0)
            logging.info('%s - Mkt cap is ZERO, found N/A data' % cmi_debug )
            wrangle_errors += 1
        else:
            mkt_cap_cl = float(re.sub('[,]', '', mkt_cap))   # remove ,
            mkt_cap_cl = round(mkt_cap_cl / 1000000, 3)                  # resize & round mantissa = 3, as nasdaq.com gives full num

        vol_abs_cl = (re.sub('[,]', '', vol_abs))                        # remove

        return wrangle_errors


####################################################################
    def build_data_list(self):
        """
        data0 & quote are class addressible accessors that this instance will populate
        No DataFrame is build.
        Build a list that holds all of our data elements.
        This list is used to write all final data into the DataFrame
        """

        # craft final data structure.
        # NOTE: globally accessible and used by quote DF and quote DICT
        symbol=co_sym_lj.rstrip()
        logging.info( f"%s - Build list for Dataframe insert: {symbol}" % cmi_debug )        # so we can access it natively if needed, without using pandas
        self.data0 = [[ \
            co_sym_lj, \
            co_name_lj, \
            arrow_updown, \
            float(price_cl), \
            price_net_cl, \
            price_pct_cl, \
            open_price_cl, \
            float(prev_close_cl), \
            float(vol_abs_cl), \
            mkt_cap_cl, \
            price_timestamp, \
            time_now ]]

        # craft the quote DICT. Doesn't hurt to do this here as it assumed that the data
        # is all nice & clean & in its final beautiful shape by now.
        symbol=co_sym_lj.rstrip()
        logging.info( f"%s - Build global dict: {symbol}" % cmi_debug )        # so we can access it natively if needed, without using pandas
        self.quote = dict( \
            symbol=co_sym_lj.rstrip(), \
            name=co_name, \
            updown=arrow_updown, \
            cur_price=price_cl, \
            prc_change=price_net_cl, \
            pct_change=price_pct_cl, \
            open_price=open_price_cl, \
            open_price_net=open_price_net, \
            open_price_pct=open_price_pct_cl, \
            prev_close=prev_close_cl, \
            vol=vol_abs_cl, \
            avg_vol=avg_vol, \
            one_year_target=oneyear_target, \
            beta=beta, \
            oneyear_hilo=LII_week_hilo, \
            mkt_cap=mkt_cap_cl )

        return 0
