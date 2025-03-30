#!/home/orville/venv/devel/bin/python3
import re
import logging
import pandas as pd
import argparse
import time
import numpy as np

from bigcharts_md import bc_quote

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class nq_wrangler:
    """
    Class to wrangle, clean, manipulate & prepare Nasdaq JSNON  Market QUote Data
    This class can only be instatiated after the JSON data has been pulled off the network.
    You can only wrangle data after you've read itoff the network. Never before!   
    """

    # global accessors
    yti = 0                    # Unique instance identifier
    qd_cycle = 0               # class thread loop counter
    args = []                  # class dict to hold global args being passed in from main() methods
    qd_quote = {}              # quote as dict
    qd_data0 = []              # JSON data payload
    quote_df0 = ""             # quote as DataFram
    qd_js_session = ""         # main requests session
    qd_quote_json0 = ""        # JSON dataset #1 : dummy_session + Update_cookiues + do_simple_get
    jsondata11 = ""            # JSON dataset #1 quote summary : passed in <-- qd_1
    jsondata20 = ""            # JSON dataset #2 quote watchlist : passed in <-- qd_2
    jsondata30 = ""            # JSON dataset #3 quote premarket : passed in <-- qd_3
    qd_quote_json4 = ""        # JSON dataset #4 quote asset_class
    path = ""
    info_url = ""
    quote_url = ""
    asset_class = ""           # global NULL TESTing indicator (important)
    summary_url = ""
    watchlist_url = ""
    premarket_url = ""

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        self.args = global_args                                # Only set once per INIT. all methods are set globally
        self.yti = yti
        return

# ###################################################################################################################################
# method 1
    def setup_zones(self, yti, qd_1, qd_2, qd_3):
        """
        Setup 3 main json class global accessors (must be passed into this method when called).
        - This means that the JSNON must be read in a JSNON data zones before setup before passed to this method
        Method must be given 3 core JSON structures (qd_1, qd_2, qd_3)
        qd_1    : jsondata11 = self.quote_json1['data']          # summary
        qd_2    : jsondata20 = self.quote_json2['data'][0]       # watchlist
        qd_3    : jsondata30 = self.quote_json3['data']          # premarket
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.setup_zones.__name__+".#"+str(self.yti)
        logging.info('%s  - build quote data payload from raw JSON' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s  - prepare json data accessors [Zone-1/Zone-2/Zone-3]...' % cmi_debug )
        self.jsondata11 = qd_1                              # summary : quote_json1['data']
        self.jsondata20 = qd_2                              # watchlist : quote_json2['data'][0]
        self.jsondata30 = qd_3                              # premarket : quote_json3['data']
        return

##########################################################################################################
    """
    Mmethods to parse nasdaq data model, test sanity for bad/missing data in json keys
    NOTE: Keys & NULLs are sometimes bad when the market is closed (e.g. premarket data). In that scenario
          this isn't an error scenario... but it's difficult logic to account for. TODO: Checking time may help
    NOTE: Checks 3 data zones in the nasdaq.com API json data model
    1. summary       :    qd_1 : self.jsondata11 = self.quote_json1['data']
    2. watchlist     :    qd_2 : self.jsondata20 = self.quote_json2['data'][0]
    3. pre-market    :    qd_3 : self.jsondata30 = self.quote_json3['data']
    """

    def z1_summary(self):
        """
        Process Zone 1 - Summary Zone
        self.asset_class must be set before this method can be called.
        """
        cmi_debug = __name__+"::"+self.z1_summary.__name__+".#"+str(self.yti)
        logging.info( f'%s   - probing zone-1 [API=summary] JSON keys/fields...' % cmi_debug )
        z = 1
        z1_errors = 0

        # TODO: I need to move away from predefined fields and just scan all the fields and create a list
        # TODO: this way, nasdaq can change their json and I wont care

        # These are the JSON keys that we are intersted in extracting. Other keys exists but their boring
        # assume that we are working on a stock (not an etf)
        jd_10 = ("OneYrTarget", "TodayHighLow", "AverageVolume", "PreviousClose", "FiftTwoWeekHighLow", "MarketCap" )
        if self.asset_class == "etf":
            jd_10 = ("MarketCap", "TodayHighLow", "FiftyDayAvgDailyVol", "PreviousClose", "FiftTwoWeekHighLow" )

        try:
            y = self.jsondata11['data']['summaryData']      # JSON struct : summary
        except TypeError:
            logging.info( f"%s   - Probe #1.1 : TypeError / BAD type @: [data][summaryData]" % cmi_debug )
            z1_errors = 1 + len(jd_10)       # everything in data set is BAD
            logging.info( f"%s   - End probing zone-1 [API=summary] / errors: {z1_errors}" % cmi_debug )
            return z1_errors
        except KeyError:
            logging.info( f"%s   - Probe #1.2 : KeyError / BAD key @: [data][summaryData]" % cmi_debug )
            z1_errors = 1 + len(jd_10)       # everything in data set is BAD
            logging.info( f"%s   - End probing zone-1 [API=summary] / errors: {z1_errors}" % cmi_debug )
            return z1_errors
        else:
            x = self.jsondata11['data']['summaryData']
            for i in jd_10:
                logging.info( f"%s   - Scaning zone-1 for Key: [{i}]" % cmi_debug )
                try:
                    y = x[i]
                except TypeError:
                    logging.info( f"%s   - Probe #1.3 : TypeError / BAD type @: [{i}] - RESET to: 0" % cmi_debug )
                    x[i]['value'] = 0      # fix the bad data by writing this field as 0
                    z1_errors += 1
                except KeyError:
                    logging.info( f"%s   - Probe #1.4 : KeyError / BAD key  @: [{i}] - RESET to: 0" % cmi_debug )
                    x[i]['value'] = 0      # fix the bad data by writing this field as 0
                    z1_errors += 1
                else:
                    z += 1
        logging.info( f"%s   - End probing zone-1 [API=summary] / errors: {z1_errors} / {len(x)} Keys" % cmi_debug )
        return z1_errors


    # ZONE #2 watchlist zone....############################################
    def z2_watchlist(self):
        """
        Process Zone 2 L watchlist
        This data zone is far more tollerant. keys/fields pre-exist. So this zone cant test for a
        non-existent/bad ticker symbol (or ETF/Fund). but this means errors are less severe.
        """
        cmi_debug = __name__+"::"+self.z2_watchlist.__name__+".#"+str(self.yti)
        logging.info( f'%s - probing zone-2 [API=watchlist] JSON keys/fields...' % cmi_debug )
        z = 1
        x = self.jsondata20['data'][0]     # JSON struct : watchlist
        jd_20 = ("symbol", "companyName", "lastSalePrice", "netChange", "percentageChange", "deltaIndicator", "lastTradeTimestampDateTime", "volume" )
        z2_errors = 0

        for i in jd_20:
            try:
                y = x[i]
            except TypeError:
                logging.info( f"%s - Probe #2.1 : TypeError / BAD type @: [{i}]" % cmi_debug )
                z2_errors += 1
            except KeyError:
                logging.info( f"%s - Probe #2.2 : KeyError / BAD key @: [{i}]" % cmi_debug )
                z2_errors += 1
            else:
                z += 1
        logging.info( f"%s - End probing zone-2 [API=watchlist] / errors: {z2_errors} / {len(x)}" % cmi_debug )
        return z2_errors

    # ZONE #3 premarket zone....########################################
    def z3_premarket(self):
        """
        Process Zone 2 - Premarket Zone
        """
        cmi_debug = __name__+"::"+self.z3_premarket.__name__+".#"+str(self.yti)
        logging.info( f'%s - probing zone-3 [API=premarket] JSON keys/fields...' % cmi_debug )
        jd30_keys = ("consolidated", "volume", "highPrice", "lowPrice", "delta" )
        #jd_30 = ("infoTable", "infoTable']['rows", "infoTable']['rows'][0", "infoTable']['rows'][0]['consolidated'",
        # NOTE: wtf  ??? "infoTable']['rows'][0]['volume'", "'infoTable']['rows'][0]['delta'" )
        z = 1
        z3_errors = 0

        try:
            y = self.jsondata30['data']['infoTable']['rows'][0]     # premarket InfoTable looks like it might may exist
        except TypeError:
            logging.info( f"%s - Probe #3.1 : TypeError BAD type @: [infoTable][rows][0]" % cmi_debug )
            z3_errors = 10               # everything in data set is BAD
            logging.info( f"%s - End probing zone-3 [API=premarket]: errors: {z3_errors}" % cmi_debug )
            return z3_errors
        except KeyError:
            logging.info( f"%s - Probe #3.2 : KeyError BAD key @: [infoTable][rows][0]" % cmi_debug )
            z3_errors = 10               # everything in data set is BAD
            logging.info( f"%s - End probing zone-3 [API=premarket]: errors: {z3_errors}" % cmi_debug )
            return z3_errors
        else:
            x = self.jsondata30['data']['infoTable']['rows'][0]
            for i in jd30_keys:     # No errors, looks reasonably healthy to start with
                try:
                    y = x[i]
                except TypeError:
                    logging.info( f"%s - Probe #3.3 : TypeError BAD type @: [{i}]" % cmi_debug )
                    z3_errors += 1
                except KeyError:
                    logging.info( f"%s - Probe #3.4 : KeyError BAD key @: [{i}]" % cmi_debug )
                    z3_errors += 1
                else:
                    z += 1
        logging.info( f"%s - End probing zone-3 [API=premarket]: errors: {z3_errors} / {len(x)}" % cmi_debug )
        return z3_errors

################################################################################################
# Quote DATA extractor ########################################################################
################################################################################################
    def do_wrangle(self):
        """
        Do a lot of work cleaning the data.
        Main flow of wrangeling & cleaning is controlled from here. All other data wrangeling
        methods are called from here. 
        """
        cmi_debug = __name__+"::"+self.do_wrangle.__name__+".#"+str(self.yti)
        wrangle_errors = 0
        null_count = 0
        a = self.z1_summary()                   # self.jsondata11 = self.quote_json1['data']
        b = self.z2_watchlist()                 # self.jsondata20 = self.quote_json2['data'][0]
        c = self.z3_premarket()                 # self.jsondata30 = self.quote_json3['data']

        if a > 0:                       # Zone 1 data in Summary is in an Abberant state
            logging.info( f'%s   - Summary Zone 1 has ERRORS: [ {a} ]' % cmi_debug )
            logging.info( f'%s   - Force a re-run to retry cleaning Summary Zone 1: [ {a} ]' % cmi_debug )
            a = self.z1_summary()    # re-run it again just to see. a should come back as == 0
            if a > 0:                   # still BAD after 2nd attempt
                logging.info( f"%s   - Nasdaq summary data is ABERRANT [ Zone 1:{a} zone 2:{b} zone 3:{c} ]" % cmi_debug )
                logging.info( f'%s   - Abandon Nasdaq quote - Data is BAD' % cmi_debug )
                wrangle_errors = a+b+c
                return wrangle_errors
            else:
                logging.info( f"%s   - Repaired ABERRANT summary data [ Zone 1:{a} zone 2:{b} zone 3:{c} ]" % cmi_debug )
                wrangle_errors += 5     # Dataset allready started out life in bad shape
                # setup main JSON data zone accessors...
                # SUMMARY quote data seem OK to pre-process for loading
                wrangle_errors = self.pre_load_z2()      # Watchlist
                wrangle_errors += self.pre_load_z3()     # Pre-market
                wrangle_errors += self.pre_load_z1()     # summary
                return wrangle_errors
        elif b > 0:         # zone 2 data in watchlist is in an Abberant state
            logging.info( f"%s   - Nasdaq watchlist data is ABERRANT [ Zone 1:{a} zone 2:{b} zone 3:{c} ]" % cmi_debug )
            logging.info( f'%s   - Abandon Nasdaq quote - Data is BAD' % cmi_debug )
            wrangle_errors = a+b+c
            return wrangle_errors
        elif c > 0:
            logging.info( f"%s   - Nasdaq premarket data is ABERRANT [ Zone 1:{a} zone 2:{b} zone 3:{c} ]" % cmi_debug )
            logging.info( f'%s   - Abandon Nasdaq quote - Data is BAD' % cmi_debug )
            wrangle_errors = self.pre_load_z2()      # Watchlist
            wrangle_errors += self.pre_load_z3()     # Pre-market
            wrangle_errors += self.pre_load_z1()     # summary
            wrangle_errors = a+b+c
            return wrangle_errors
        else:
            logging.info( f"%s   - Good NOMINAL data state [ Zone 1: {a} zone 2: {b} zone 3: {c} ]" % cmi_debug )
            wrangle_errors += 5     # Dataset allready started out life in bad shape
            wrangle_errors = self.pre_load_z2()      # Watchlist
            wrangle_errors += self.pre_load_z3()     # Pre-market
            wrangle_errors += self.pre_load_z1()     # summary
            return wrangle_errors
            wrangle_errors += 50
            # a = z1_summary()   : zone 1
            # b = z2_watchlist() : zone 2
            # c = z3_premarket() : zone 3
        return wrangle_errors

#######################################################################################
# Zone 2 : WATCHLIST quote data
    def pre_load_z2(self):
        """
        NOTE: This is a helper method for do_wrangle()
        NOTE: No need to ever call this explicitly. - that will #fail
        """
        cmi_debug = __name__+"::"+self.pre_load_z2.__name__+".#"+str(self.yti)
        if self.jsondata20['data'] is not None:                                # bad payload? - can also test b == 0
            logging.info('%s  - zone-2 [watchlist] : Accessing JSON data fields...' % cmi_debug )
            jd20 = self.jsondata20['data'][0]                            # HEAD of data payload
            self.co_sym = jd20['symbol']                                  # "IBM"
            self.co_name = jd20['companyName']                                 # "International Business Machines Corporation Common Stock"
            self.price = jd20['lastSalePrice']                                 # "$143.32"
            self.price_net = jd20['netChange']                                 # "+4.39"
            self.price_pct = jd20['percentageChange']                          # "3.16%"
            self.arrow_updown = jd20['deltaIndicator']                         # "up"
            self.price_timestamp = jd20['lastTradeTimestampDateTime']          # "2021-10-01T00:00:00"
            self.vol_abs = jd20['volume']                                      # "6,604,064"
            logging.info( '%s  - zone-2 [watchlist] : [8] fields - Done' % cmi_debug )
            return 0
        else:
            logging.info('%s  - zone-2 [watchlist] : BAD json payload - NOT regular stock / Abort' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            return 99

#######################################################################################
# Zone 3 : PRE-MARKET quote data - 2 data zones
    def pre_load_z3(self):
        """
        NOTE: This is a helper method for do_wrangle()
        NOTE: No need to ever call this explicitly. - that will #fail
        """
        cmi_debug = __name__+"::"+self.pre_load_z3.__name__+".#"+str(self.yti)
        logging.info('%s  - zone-3 [pre-market] : Accessing data fields...' % cmi_debug )
        if self.jsondata30['data'] is not None:                                # bad payload? - can also test c == 0
            jsondata30 = self.jsondata30['data']                               # HEAD of data payload 0
            try:
                jsondata31 = self.jsondata30['data']['infoTable']['rows'][0]       # HEAD of data payload 1
            except TypeError:
                logging.info('%s  - zone-3 [pre-market] : WARNING infoTable payload is BAD / Zero ALL data' % cmi_debug )        # bad symbol json payload
                self.open_price = "$0.0 0.0 0.0"
                self.open_volume = 0                                  # e.g. "71,506"
                self.open_updown = "N/A"                              # e.g. "up"
                return 99
            else:
                self.open_price = jsondata31['consolidated']                             # WARN: open_price info = multi-field string needs splitting e.g. "$140.8 +1.87 (+1.35%)"
                self.open_volume = jsondata31['volume']                                  # e.g. "71,506"
                self.open_updown = jsondata31['delta']                                   # e.g. "up"
                logging.info( '%s  - zone-3 [pre-market] : [3] fields - Done' % cmi_debug )
                return 0
        else:
            logging.info('%s  - Zone-3 [pre-market] : BAD json payload - NOT regular stock / Abort' % cmi_debug )        # bad symbol json payload
            self.quote.clear()
            return 99

###############################################################################################3
# Zone 1 : Summary Zone
    def pre_load_z1(self):
        """
        NOTE: This is a helper method for do_wrangle()
        NOTE: No need to ever call this explicitly. - that will #fail
        NOTE: This data zone is highly fragile and intollerant of net get() errors. It constantly
              contains lots of errors, missing fiels, bad fields etc. 
              This is why we process it last !!!
        """
        cmi_debug = __name__+"::"+self.pre_load_z1.__name__+".#"+str(self.yti)
        logging.info('%s  - zone-1 [summary] : Accessing JSON data fields...' % cmi_debug )
        if self.asset_class == "stocks":
            fields_set = 0
            if self.jsondata11['data'] is not None:                    # bad payload? - can also test a == 0
                j11 = self.jsondata11['data']['summaryData']           # HEAD of data payload
                self.prev_close = j11['PreviousClose']['value']        # e,g, "$138.93"
                self.mkt_cap = j11['MarketCap']['value']               # e.g. "128,460,592,862"
                self.today_hilo = j11['TodayHighLow']['value']         # WARN: multi-field string needs splitting/wrangeling e.g. "$143.97/$140.37"
                self.avg_vol = j11['AverageVolume']['value']           # e.g. "4,811,121" or N/A
                self.oneyear_target = j11['OneYrTarget']['value']      # e.g. "$151.00"
                fields_set = 5
                logging.info( f"%s  - zone-1 [summary] : {fields_set} / {len(j11)} fields - Done" % cmi_debug )
                return 0
            else:
                logging.info( '%s  - zone-1 / [summary] : BAD json payload - BAD stock data' % cmi_debug )        # bad symbol json payload
                self.quote.clear()
                return 99
        else:
            logging.info( f"%s  - zone-1 [summary] : Not a stock - skipping some data..." % cmi_debug )
            j11 = self.jsondata11['data']['summaryData']           # HEAD of data payload
            self.avg_vol = 0                                    # not stock gets 0 here
            self.oneyear_target = 0                             # not stock gets 0 here
            self.prev_close = j11['PreviousClose']['value']        # e,g, "$138.93"
            self.mkt_cap = j11['MarketCap']['value']               # e.g. "128,460,592,862"
            self.today_hilo = j11['TodayHighLow']['value']         # WARN: multi-field string needs splitting/wrangeling e.g. "$143.97/$140.37"
            fields_set = 3
            logging.info( f"%s  - zone-1 [summary] : {fields_set} / {len(j11)} fields - Done" % cmi_debug )
            return 1

########################################################################################
# wrangle, clean, cast & prepare the data ##############################################
    def clean_cast(self):
        """
        This method is a LINEAR run down all known data elements
        Just try and process the data as fast as possible
        All variavble are loaded in support of creating a Qoute DataFram
        At the end just return a count of how many wrangle Errors we encountered
        """
        cmi_debug = __name__+"::"+self.clean_cast.__name__+".#"+str(self.yti)
        logging.info('%s   - Begin data cleanse for final setup...' % cmi_debug )
        # >>> DEBUG Xray <<<
        if self.args['bool_xray'] is True:
            print ( f"\n================= Nasdaq quote data : raw uncleansed =================" )
            work_on = ['self.co_sym', 'self.co_name', 'self.price', 'self.price_net', 'self.price_pct', 'self.arrow_updown', \
                    'self.price_timestamp', 'self.vol_abs', 'self.open_price', 'self.open_volume', 'self.open_updown', \
                    'self.prev_close', 'self.mkt_cap', 'self.today_hilo', 'self.avg_vol', 'self.oneyear_target', 'self.prev_close']
            xx = iter(work_on)
            for name in work_on:
                print ( f"{next(xx)} / {eval(name)}" )
        # >>> DEBUG Xray <<<
        cc_errors = 0
        #################################### Begin Deep clean ##########################################
        self.co_sym_lj = self.co_sym.strip()
        #co_sym_lj = np.array2string(np.char.ljust(co_sym, 6) )          # left justify TXT & convert to raw string
        self.co_name_lj = (re.sub('[\'\"]', '', self.co_name) )                    # remove " ' and strip leading/trailing spaces
        self.co_name_lj = np.array2string(np.char.ljust(self.co_name_lj, 25) )     # left justify & convert to raw string
        self.co_name_lj = (re.sub('[\']', '', self.co_name_lj) )                   # remove " ' and strip leading/trailing spaces

        if self.price == "N/A":
            self.price_cl = float(0)
            logging.info('%s - Price is bad, found N/A data' % cmi_debug )
            cc_errors += 1
        else:
            self.price_cl = (re.sub('[ $,]', '', self.price))                      # remove $ sign
            self.price_cl = round(float(self.price_cl), 2)

        if self.price_net == "N/A":
            self.price_net_cl = float(0)
            logging.info('%s - Price NET is bad, found N/A data' % cmi_debug )
            cc_errors += 1
        elif self.price_net == 'UNCH':
            self.price_net_cl = float(0)
            logging.info('%s - Price NET is unchanged' % cmi_debug )
            cc_errors += 1
        else:
            self.price_net_cl = (re.sub('[\-+]', '', self.price_net))              # remove - + signs
            self.price_net_cl = float(self.price_net)

        if self.price_pct == "N/A":
            self.price_pct_cl = float(0)
            logging.info('%s - Price pct is bad, found N/A data' % cmi_debug )
            cc_errors += 1
        elif self.price_pct == "UNCH":
            self.price_pct_cl = float(0)
            logging.info('%s - Price pct is unchanged' % cmi_debug )
            cc_errors += 1
        elif self.price_pct == '':
            self.price_pct_cl = float(0)
            logging.info('%s - Price pct is bad, field is Null/empty' % cmi_debug )
            cc_errors += 1
        else:
            self.price_pct = (re.sub('[\-+%]', '', self.price_pct))                # remove - + % signs
            self.price_pct_cl = float(self.price_pct)

        # ################# open price(s) need extra treatment & care...
        """
        Open_price data elements are 3 fields concatinted into 1 long string / e.g. $140.8 +1.87 (+1.35%)
        This is a bad nasdaq strategy. We must split & post-process/wrangle the split fields
        """
        if self.open_price == "N/A" or self.open_price is None:
                """ Stage #0 """
                logging.info( f'%s - BAD open_price compound data: {type(self.open_price)} / {self.open_price} / set all to 0.0' % cmi_debug )
                self.open_price_cl = float(0)
                self.open_price_net = float(0)
                self.open_price_pct_cl = float(0)
                cc_errors += 3
        else:       # data is good...access 3 indices of sub-data from split list[]
            self.ops = self.open_price.split()
            logging.info( f"%s - Split open_price into {len(self.ops)} fields" % cmi_debug )

            """ Stage #1 """
            try:
                self.open_price = self.ops[0]                     # e.g. 140.8
            except IndexError:
                logging.info( f'%s - Bad key open_price: {type(self.open_price)} / setting to $0.0 / {self.open_price}' % cmi_debug )
                self.open_price = float(0)
                cc_errors += 1
            except ValueError:
                logging.info( f'%s - Bad open_price: {type(self.open_price)} / setting to $0.0 / {self.open_price}' % cmi_debug )
                self.open_price = float(0)
                cc_errors += 1
            else:
                self.open_price_cl = (re.sub('[ $,]', '', self.ops[0]))   # remove " " $ ,
                self.open_price_cl = float(self.open_price_cl)
                """ Stage #2 """

            if len(self.ops) != 1:   # the split failed to seperate all 3 elements. i.e. open_price_net & open_price_pct don't exist
                try:    # data is good...keep processing...
                    self.open_price_net = self.ops[1]                 # (test for missing data) - good data =  +1.87
                except IndexError:
                    logging.info( f'%s - Bad key open_price_net: {type(self.open_price_net)} / setting to $0.0 / {self.open_price_net}' % cmi_debug )
                    self.open_price_net = float(0)               # set NULL data to ZERO
                    cc_errors += 1
                except ValueError:
                    logging.info( f'%s - Bad open_price_net: {type(self.open_price_net)} / setting to $0.0 / {self.open_price_net}' % cmi_debug )
                    self.open_price_net = float(0)               # set NULL data to ZERO
                    cc_errors += 1
                except TypeError:
                    logging.info( f'%s - Bad open_price_net: {type(self.open_price_net)} / setting to $0.0 / {self.open_price_net}' % cmi_debug )
                    self.open_price_net = float(0)               # set NULL data to ZERO
                    cc_errors += 1
                else:
                    pass    # data is good...keep processing...
                    # INFO: no need of clean open_price_net - VAR is currently not used n our data model
                    """ Stage #3 """
                    try:
                        self.open_price_pct = self.ops[2]                 # (test for missing data) - good data = e.g. (+1.35%)"
                    except IndexError:
                        logging.info( f'%s - Bad key open_price_pct: {type(self.open_price_pct)} / setting to $0.0 / {self.open_price_pct}' % cmi_debug )
                        self.open_price_pct = float(0)               # set NULL data to ZERO
                        cc_errors += 1
                    except ValueError:
                        logging.info( f'%s - Bad open_price_pct: {type(self.open_price_pct)} / setting to $0.0 / {self.open_price_pct}' % cmi_debug )
                        self.open_price_pct = float(0)               # set NULL data to ZERO
                        cc_errors += 1
                    else:
                        self.open_price_pct_cl = (re.sub('[)(%]', '', self.price_pct))        # # remove " ", %  (leave +/- indicator)
                        # INFO: no need of clean open_price_net - VAR is currently not used n our data model
                        logging.info( f"%s - All 3 open_price vars sucessfully split & processed" % cmi_debug )
            else:
                self.open_price_net = float(0)
                self.open_price_pct_cl = float(0)

        #################################################
        if self.prev_close == "N/A":
            self.prev_close_cl = 0
            logging.info('%s - Prev close is bad, found N/A data' % cmi_debug )
            cc_errors += 1
        else:
            self.prev_close_cl = (re.sub('[ $,]', '', self.prev_close))   # remove $ sign

        if self.mkt_cap == "N/A":
            self.mkt_cap_cl = float(0)
            logging.info('%s - Mkt cap is bad, found N/A data' % cmi_debug )
            cc_errors += 1
        elif self.mkt_cap == 0:
            self.mkt_cap_cl = float(0)
            logging.info('%s - Mkt cap is ZERO, found N/A data' % cmi_debug )
            cc_errors += 1
        else:
            self.mkt_cap_cl = float(re.sub('[,]', '', self.mkt_cap))   # remove ,
            self.mkt_cap_cl = round(self.mkt_cap_cl / 1000000, 3)                  # resize & round mantissa = 3, as nasdaq.com gives full num

        self.vol_abs_cl = (re.sub('[,]', '', self.vol_abs))                        # remove

        return cc_errors


####################################################################
    def build_data_sets(self):
        """
        qd_data0 & quote are class addressible accessors that this instance will populate
        and a class addressible DataFrame is built.
        Build a list that holds all of our data elements.
        This list is used to write all final data into the DataFrame
        """
        cmi_debug = __name__+"::"+self.build_data_sets.__name__+".#"+str(self.yti)
        # craft final data structure.
        # NOTE: globally accessible and used by quote DF and quote DICT

        self.time_now = time.strftime("%H:%M:%S", time.localtime() )
        self.symbol=self.co_sym_lj.rstrip()
        logging.info( f"%s - Build list for Dataframe insert: {self.symbol}" % cmi_debug )        # so we can access it natively if needed, without using pandas
        self.qd_data0 = [[ \
            self.co_sym_lj, \
            self.co_name_lj, \
            self.arrow_updown, \
            float(self.price_cl), \
            float(self.price_net_cl), \
            float(self.price_pct_cl), \
            float(self.open_price_cl), \
            float(self.prev_close_cl), \
            float(self.vol_abs_cl), \
            self.mkt_cap_cl, \
            self.price_timestamp, \
            self.time_now ]]

        # craft the quote DICT. Doesn't hurt to do this here as it assumed that the data
        # is all nice & clean & in its final beautiful shape by now.
        self.symbol=self.co_sym_lj.rstrip()
        logging.info( f"%s - Build global dict: {self.symbol}" % cmi_debug )        # so we can access it natively if needed, without using pandas
        self.qd_quote = dict( \
            symbol=self.co_sym_lj.rstrip(), \
            name=self.co_name, \
            updown=self.arrow_updown, \
            cur_price=float(self.price_cl), \
            prc_change=float(self.price_net_cl), \
            pct_change=float(self.price_pct_cl), \
            open_price=float(self.open_price_cl), \
            open_price_net=float(self.open_price_net), \
            open_price_pct=self.open_price_pct_cl, \
            prev_close=self.prev_close_cl, \
            vol=self.vol_abs_cl, \
            avg_vol=self.avg_vol, \
            one_year_target=self.oneyear_target, \
            mkt_cap=self.mkt_cap_cl )

        logging.info( f"%s - Build global DF: {self.symbol}" % cmi_debug )
        logging.info( '%s  - Drop ephemeral DF' % cmi_debug )
        #self.quote_df0.drop(self.quote_df0.index, inplace=True)        # ensure the DF is empty
        logging.info('%s - Populate DF with new quote data' % cmi_debug )
        self.quote_df0 = pd.DataFrame(self.qd_data0, columns=[ 'Symbol', 'Co_name', 'arrow_updown', 'Cur_price', 'Prc_change', 'Pct_change', 'Open_price', 'Prev_close', 'Vol', 'Mkt_cap', 'Exch_timestamp', 'Time' ] )
        logging.info('%s - Quote DF created' % cmi_debug )

        return 0