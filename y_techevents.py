#! python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import argparse
import time

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class y_techevents:
    """
    Class to extract Simple Today/Short/Medium/Long term indicator data set from finance.yahoo.com
    """

    # global accessors
    symbol = ""         # class global
    te_sentiment = {}   # Dict contains Tech Events elements...e.g.
                        # 0: ("today_only", "1D", Bullish/Bearish/Neutral or N/A )
                        # 1: ("short_term", "2W - 6W", Bullish/Bearish/Neutral or N/A )
                        # 2: ("med_term", "6W - 9M", Bullish/Bearish/Neutral or N/A )
                        # 3: ("long_term", "9M+", Bullish/Bearish/Neutral or N/A )
                        # 4: count_of_Bullish
                        # 5: Tech sentiment computed ranking
    te_df0 = ""
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
        self.te_df0 = pd.DataFrame(columns=[ 'Symbol', 'Today', 'Short', 'Mid', 'Long', 'Bullcount', 'Senti', 'Time' ] )  # init empty DF with preset columns
        self.yti = yti
        return

#######################################################################
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
        #self.te_all_url = "https://finance.yahoo.com/quote/" + self.symbol + "?p=" + self.symbol + "&.tsrc=fin-srch"
        self.te_all_url = "https://finance.yahoo.com/quote/" + self.symbol
        self.te_short_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=short"
        self.te_mid_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=intermediate"
        self.te_long_url = "https://finance.yahoo.com/chart/" + self.symbol + "?Technical=long"
        #
        # 2024 new URL's
        # https://finance.yahoo.com/chart/T

        logging.info( f"================================ Tech Events API endpoints ================================" )
        logging.info( f"{cmi_debug} - API endpoint #0: [ {self.te_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #1: [ {self.te_all_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #2: [ {self.te_short_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #3: [ {self.te_mid_url} ]" )
        logging.info( f"{cmi_debug} - API endpoint #4: [ {self.te_long_url} ]" )
        return

###########################################################################
# method #2
    def get_te_zones(self, me):
        """
        Connect to finance.yahoo.com and extract (scrape) the raw JSON data out of
        the embedded webpage [finance.yahoo.com/chart/GOL?technical=short] html data table.
        Sabe JSON to class global attribute: self.te_resp0.text
        """
        cmi_debug = __name__+"::"+self.get_te_zones.__name__+".#"+str(self.yti)+"."+str(me)
        logging.info( f"{cmi_debug} - IN : {self.te_all_url}" )
        with requests.get( self.te_all_url, stream=True, timeout=5 ) as self.te_resp0:
            logging.info( f"{cmi_debug} - get() data / storing..." )
            self.soup = BeautifulSoup(self.te_resp0.text, 'html.parser')
            logging.info( f"{cmi_debug} - Zone #1 / [Entire page] {len(self.soup)} lines extracted / Done" )

        logging.info( f"{cmi_debug} - Zone #2 / search [ul zones]..." )
        #self.te_zone = self.soup.find_all(attrs={"id": "dropdown-menu"} )
        self.te_zone = self.soup.find_all("ul")
        logging.info( f"{cmi_debug} - zone #2 / [ul zones] found: {len(self.te_zone)}" )

        #logging.info( f"{cmi_debug} - Zone #2\n{self.te_zone}" )
        #logging.info( f"{cmi_debug} - Zone #3 / Tech Events zone [tag: <li>]..." )


        self.te_lizones = self.te_zone.li
        logging.info( f"{cmi_debug} - >>>DEBUG<<< Zone #3 / [li zones]: {len(self.te_lizones)}" )
        print ( f">>>DEBUG:<<< {self.te_lizones}" )

        try:
            self.te_lizones = self.te_zone.find_all("li")
            logging.info( f"{cmi_debug} - Zone #3 / [li zones]: {len(self.te_lizones)}" )
        except AttributeError as ae_inst:       # ae_inst = my custom AE var
            if ae_inst.__cause__ is None:       # interrogate error raised - was it for [NoneType]
                logging.info( f"{cmi_debug} - Zone #3 / [li tag] BS4 search failed: None" )
                return -1
            else:
                logging.info( f"{cmi_debug} - Zone #3 / [li tag] Attribute ERROR: {ae_inst.__cause__}" )
                return -2
        else:
            logging.info( f"{cmi_debug} - Zone #4: Embeded Data block [label tag]" )
            self.bb_datablock = self.te_zone.find_all('label')
            #self.bb_today = self.te_zone.find(attrs={"class": "W(1/4)--mobp W(1/2) IbBox"} )
            return 0                            # success

###########################################################################
# method #3
    def build_te_data(self, me):
        """
        Build out BULLISH/BEARISH/NEUTRAL Perfromance Outlook Technical Events ranking for each symbol
        Rankings are weighted, depending on which timeframe this Bull/Bear/Neutral indicator relates to (i.e. today/short/med/long term)
        - Weightings can get complicated: e.g. ...
            : Short term Bullish -> more weighting than Long term Bullish
            : Bullish today, _> more weighting than Bullish short term
            : Neutral short term -> more weighting than Neutral Long term
            : etc, etc... (see bb_weights DICT)

        Dict structure: { key: (embeded 5 element tuple) }
        e.g. {0: (te_sml, te_timeframe, "Grey", "Sideways", "Neutral") }
            1.  tme_sml : (Short/Medium/Long)
            2.  tm_timeframe : Time frame that this Tech Event covers (days/weeks/months)
            3.  Tech Event Indicator: Red/Grey/Green   * not included in final dict
            4.  Tech Event Indicator: Down/Sideways/Up *  not included in final dict
            5.  Tech Event Indicator: Bearish/Neutral/Bullish

        """
        #logging.disable(0)                  # ENABLE Log level = INFO
        #logging.disable(20)                 # DISABLE Logging

        cmi_debug = __name__+"::"+self.build_te_data.__name__+".#"+str(self.yti)+"."+str(me)
        logging.info( f"{cmi_debug} - CALLED" )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info( f"{cmi_debug} - Scan Tech Event indicators" )
        bullcount = 0    # counter / how many BULLISH rankings for this symbol
        rankalgo = 0     # FINAL Bull/Bear ranking value assigned to this symbol
        y = 0            # current dict key/index (i.e. column we are working on..today/short/med/long)


        ########################################################################################
        # Internal helper method
        def algo_te_autorank(bull_bear, y, te_sml, rankalgo, te_timeframe, bullcount):
            # PRIVATE: Helper method, since we do this 4 x ~50 ticker_sybols
            #       figurre out which Technical indiciator we are looking at, which column we
            #       are in, and what the current Bill_Bear code is...: then track some stats & store
            #       this data in some important places
            #       bull_bear:
            #               Bullish, Bearish, Neutral, N/A
            te_bb_state = bull_bear
            y = y
            te_sml = te_sml
            rankalgo = rankalgo
            bullcount = bullcount
            te_timeframe = te_timeframe
            logging.info( f"{cmi_debug} - #1 - y_col:{y} / looking for term: {te_sml} / decoded into:{bb_term.get(te_sml)}" )
            te_term = bb_term.get(te_sml)               # decode yahoo time period -> Short_Med_Long_N/A
            bb_getrank = bb_weights.get(te_bb_state)    # select DICT index that matches timeframe : result -> DICT
            z = bb_getrank.get(te_term)                 # get algo ranking weight for this col/term timeframe
            logging.info( f"{cmi_debug} - #1 - y_col:{y} / te_term:{te_term}: / BB_state:{te_bb_state} / algo rank:{z}" )
            rankalgo += z                               # set ranking
            self.te_sentiment.update({y: (te_sml, te_timeframe, te_bb_state)} )
            if bull_bear is 'Bullish': bullcount += 1
            y += 1                                      # incr dict/index (timeframe column)
            return (y, rankalgo, bullcount)

        ####################################################
        # algo hinter DICT to decode Techncial weightings
        # We can customize these as we see fit
        bb_weights = { 'Bullish': {'Today': 5, 'Short': 4, 'Med': 4, 'Long': 4},
                        'Neutral': {'Today': 2, 'Short': 1, 'Med': 1, 'Long': 1},
                        'N/A': {'Today': 0, 'Short': 0, 'Med': 0, 'Long': 0},
                        'Bearish': {'Today': -5, 'Short': -4, 'Med': -3, 'Long': -2}
                        }

        ####################################################
        # algo hinter DICT to decode data range terminology
        bb_term = { 'Today': 'Today',
                    'Short Term (2-3 weeks)': 'Short',
                    'Mid Term (6 weeks - 9 months)': 'Med',
                    'Long Term (9+ months)': 'Long',
                    'N/A': 'N/A'
                    }

        ######################################################################################
        # BEGIN : Auto ranking algo
        # TODAY is treated slightly differnt, becasue its the FIRST element & we know this...no need to guess col/pos
        """ bb_today = self.bb_today.next_element.next_element.string    # get the Bull/Bear sentimewnt
        self.te_sentiment.update({y: ("Today", "1D", bb_today)} )
        te_term = bb_term.get('Today')                     # decode yahoo time periods -> Short_Med_Lon_N/A
        bb_getrank = bb_weights.get(bb_today)              # select DICT index that matches timeframe : result -> DICT
        z = bb_getrank.get(te_term)                        # get algo ranking weight for this col/term tag (which is TODAY)
        logging.info( f"{cmi_debug} - #0 - y_col:{y} / te_term:{te_term}: / BB_state:{bb_today} / algo rank:{z}" )
        timeframe_window = bb_weights.get(bb_today)        # get tupple @ index = Bull-Bear State
        rankalgo += z                                      # set rank weighting for @pos TODAY
        logging.info( f"{cmi_debug} - #0 - y_col:{y} / bb_today:{bb_today} / rank:{rankalgo}" )
        if bb_today == "Bullish": bullcount += 1           # keep count of BULLISH
        """

        # CONTINUE : ranking/weighting algo
        # figurre out what COL we are in, what the BB status is and apply a weighting from HINTER table
        y += 1                               # done with TODAY . incr dict key/index to next timeframe
        z = 0                                # reset ranking
        #for j in self.te_lizones:           # eval historical sentiments across all timeframes
        for j in self.bb_datablock:          # eval historical sentiments across all timeframes
            for i in j:
                te_strings = i.strings
                te_timeframe = next(te_strings)   # Timeframe string... "Short Term (2-3 weeks)", "Mid Term (6 weeks - 9 months)", "Long Term (9+ months)"
                te_sml = next(te_strings)         # Tech sentiment string... Bullish, Neutral, Bearish
                print ( f">>>>>DEBUG: sentiment: {te_sml} <<<<<" )
                algo_te_autorank(te_sml, y, te_sml, rankalgo, te_timeframe, bullcount)

                """
                 if i.svg is not None:
                    red = i.svg.parent.contents
                    red_down = re.search('180deg', str(red) )
                    grey_neutral = re.search('90deg', str(red) )
                    if red_down:             # Red = Bearish
                        y, rankalgo, bullcount = algo_te_autorank('Bearish', y, te_sml, rankalgo, te_timeframe, bullcount)
                    elif grey_neutral:      # Grey = Neutral
                        y, rankalgo, bullcount = algo_te_autorank('Neutral', y, te_sml, rankalgo, te_timeframe, bullcount)
                    else:                  # Green = Bullish
                        y, rankalgo, bullcount = algo_te_autorank('Bullish', y, te_sml, rankalgo, te_timeframe, bullcount)
                else:
                    pass
                    y, rankalgo, bullcount = algo_te_autorank('N/A', y, te_sml, rankalgo, te_timeframe, bullcount)
                    z = 0
                """

        self.te_sentiment.update({y: bullcount} )
        y += 1         # advance dict pointer
        self.te_sentiment.update({y: rankalgo} )
        logging.info('%s - populated new Tech Event dict' % cmi_debug )
        #logging.disable(0)                   # ENABLE Logging
        #logging.disable(20)                  # DISABLE Logging
        return y        # number of rows inserted into Tech events dict

###########################################################################
# method #4
    def build_te_summary(self, te_combo_df, me):
        """
        Build a Performance Outlook Technical Events DataFrame that is...
        A nice easy to read summary table
        With Quick to identify stats on BUllish/Bearish Outlook
        And can be quickly visually correlated to the Master Summary DataFrame
        """
        cmi_debug = __name__+"::"+self.build_te_summary.__name__+".#"+str(self.yti)+"."+str(me)

        logging.info( f"{cmi_debug} - get combo_df uniques" )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        #DEBUG
        print ( f"COMBO_DF: {te_combo_df}" )
        te_source = te_combo_df.list_uniques()    # work on the combo DataFrame (unique only, no DUPES)

        cols = 1
        print ( f"\n===== Build Bullish/Bearish outlook summary ==============================" )
        for this_sym in te_source['Symbol'].tolist():       # list of symbols to work on
            nq_symbol = this_sym.strip().upper()            # clearn each symbol (DF pads out with spaces)
            print ( f"{this_sym}...", end="", flush=True )
            self.form_api_endpoints(nq_symbol)
            te_status = self.get_te_zones(me)
            if te_status != 0:                              # FAIL : cant get te_zone data
                self.te_is_bad()                            # FAIL : build a FAILURE dict
                self.build_te_df(me)                        # FAIL: insert failure status into DataFrame for this symbol
                print ( f"!", end="", flush=True )
                logging.info( f"{cmi_debug} - FAILED to get Tech Event data: Clear all dicts" )
                self.te_sentiment.clear()
                cols += 1
            else:
                print ( f"+", end="", flush=True )          # GOOD : suceeded to get TE indicators
                self.build_te_data(me)                      # extract Tech Events data elements
                self.build_te_df(me+1)                      # debug helper, since we call method multiple times
                cols += 1

            if cols == 8:
                print ( f" " )              # only print 8 symbols per row
                cols = 1
            else:
                print ( f" / ", end="", flush=True )
            self.te_sentiment.clear()

        return

###########################################################################
# method #5
    def te_is_bad(self):
        """
        Build a Technical Events dict showing all [ BAD / N/A ] indicators
        This method is leveraged if we experince issues scraping the TE indicators from the
        the Tech performance page/zones becasue they are flakey & unreliable. (yahoo wants you
        to pay for premium serivce to get access to them). Also, some tickers dont contain TE data
        (for example: some ETF's, Funds, Trusts)
        Dict structure: { key: (embeded 5 element tuple) }
        e.g. {0: (te_sml, te_timeframe, "Grey", "Sideways", "Neutral") }
        1.  tme_sml : (Short/Medium/Long)
        2.  tm_timeframe : Time frame that this Tech Event covers (days/weeks/months)
        3.  Tech Event Indicator: - set to N/A
        4.  Tech Event Indicator: - set to N/A
        5.  Tech Event Indicator: - set to N/A
        """
        cmi_debug = __name__+"::"+self.te_is_bad.__name__+".#"+str(self.yti)

        logging.info( f"{cmi_debug} - CALLED" )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info( f"{cmi_debug} - Set ALL Tech Event indicators to BAD: N/A and 0" )
        bb_today = "N/A"
        self.te_sentiment.update({0: ("today_only", "1D", "N/A")} )
        self.te_sentiment.update({1: ("short_term", "2W - 6W", "N/A")} )
        self.te_sentiment.update({2: ("med_term", "6W - 9M", "N/A")} )
        self.te_sentiment.update({3: ("long_term", "9M+", "N/A")} )
        self.te_sentiment.update({4: 0})
        self.te_sentiment.update({5: 0})
        logging.info( f"{cmi_debug} - populated dict as BAD data: All values set to N/A" )
        return 4        # number of rows inserted into Tech events dict

###########################################################################
# method #6
    def build_te_df(self, me):
        """
        Add a ROW into the sentiment DataFrame
        ROW is for current symbol last worked on, so method must *only* be called after
        you have sucessfullu built & populated the Tech Events sentiment dict.
        """

        cmi_debug = __name__+"::"+self.build_te_df.__name__+".#"+str(self.yti)+"."+str(me)
        logging.info( f"{cmi_debug} - CALLED" )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info( f"{cmi_debug} - Create Tech Event Perf DataFrame" )
        ####################################################################
        # craft final data structure.
        # NOTE: globally accessible and used by quote DF and quote DICT
        logging.info( f"{cmi_debug} - Build Dataframe dataset: {self.symbol}" )        # so we can access it natively if needed, without using pandas
        data0 = [[ \
           self.symbol, \
           self.te_sentiment[0][2], \
           self.te_sentiment[1][2], \
           self.te_sentiment[2][2], \
           self.te_sentiment[3][2], \
           self.te_sentiment[4], \
           self.te_sentiment[5], \
           time_now ]]
        # self.te_df0.drop(self.te_df0.index, inplace=True)        # ensure the DF is empty
        logging.info( f"{cmi_debug} - Populate DF with Tech Events emphemerial dict data" )

        self.df_1_row = pd.DataFrame(data0, columns=[ 'Symbol', 'Today', 'Short', 'Mid', 'Long', 'Bullcount', 'Senti', 'Time' ] )
        self.te_df0 = pd.concat([self.te_df0, self.df_1_row])
        #self.te_df0 = self.te_df0.append(te_temp_df0, ignore_index=True)
        logging.info( f"{cmi_debug} - Tech Event DF created" )

        return

###########################################################################
# method #7
    def reset_te_df0(self):
        """
        Reset DataFrame index to be sequential, sarting from 0
        """
        cmi_debug = __name__+"::"+self.reset_te_df0.__name__+".#"+str(self.yti)
        logging.info( f"{cmi_debug} - CALLED" )
        self.te_df0.reset_index(inplace=True, drop=True)
        logging.info( f"{cmi_debug} - completed" )
        return

###########################################################################
# method #8
    def te_into_nquote(self, nqinst):
        """
        Push the Tech Event Bull/Bear Indicators into their location within the nasdaq quote dict
        which is now owned by the nasdaq_wrangler::nq_wrangler class in the accessor dict {} - qd_quote
        NOTE: This is .update is BAD form b/c we reshape the dict struct of qd_quote{} so that it no longer
              matches the original defiend shape in the class where its managed (nasdaq_wrangler::nq_wrangler)
        """
        cmi_debug = __name__+"::"+self.te_into_nquote.__name__+".#"+str(self.yti)
        logging.info( f"{cmi_debug} - CALLED" )
        nqinst.update({"today_only": self.te_sentiment[0][2]} )
        nqinst.update({"short_term": self.te_sentiment[1][2]} )
        nqinst.update({"med_term": self.te_sentiment[2][2]} )
        nqinst.update({"long_term": self.te_sentiment[3][2]} )
        nqinst.update({"Bull_count": self.te_sentiment[4]} )
        nqinst.update({"Senti_algo": self.te_sentiment[5]} )
        logging.info( f"{cmi_debug} - completed" )
        return
