#!/home/orville/venv/devel/bin/python3
import urllib.request
import pandas as pd
import logging
import argparse

# logging setup
logging.basicConfig(level=logging.INFO)

# my private classes & methods
from nasdaq_quotes import nquote
from nasdaq_wrangler import nq_wrangler

#####################################################
# CLASS
class combo_logic:
    """
    Do deeper logic data cleaning & thinking across multiple dataframes.
    Although this is not considerd DEEP Logic, Machine Learning, or AI.
    """
    deep_1 = ""
    deep_2 = ""
    deep_3 = ""
    inst_uid = 0
    combo_df = ""
    combo_dupes = ""
    min_price = {}      # Heler: DICT to help find cheapest ***HOT stock
    args = []           # class dict to hold global args being passed in from main() methods
    rx = []             # hottest stock with lowest price overall

    cx = { 'LT': 'Mega cap + % gainer', \
        'LB': 'L cap + % gainer', \
        'LM': 'M cap + % gainer', \
        'LZ': 'Zero L cap + % gainer', \
        'SB': 'B/S cap + % gainer', \
        'SM': 'S cap + % gainer', \
        'SZ': 'Zero S cap + % gainer', \
        'EF': 'ETF Fund Trust + % gainer', \
        'UZ': '? cap + % gainer', \
        'TM': 'T cap + % gainer',
        }

    def __init__(self, yti, d1, d2, d3, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INST_class' % cmi_debug )
        self.inst_uid = yti
        self.deep_1 = d1.tg_df1.drop(columns=[ 'ERank', 'Time' ]).sort_values(by='Pct_change', ascending=False )
        self.deep_2 = d2.dg1_df1.drop(columns=[ 'Row', 'Time' ] )
        self.deep_3 = d3.up_df0.drop(columns=[ 'Row', 'Time', 'Vol', 'Vol_pct']).sort_values(by='Pct_change', ascending=False )
        self.args = global_args
        return

    def __repr__(self):
        return ( f'{self.__class__.__name__}(' f'{self.inst_uid!r})' )

#############################################################################
# method #0

    def prepare_combo_df(self):
        """
        combo_df is the **Single Source of Truth** dataset.
        It is used & referenced by a lot of methods, functions and stuff.
        """
        cmi_debug = __name__+"::"+self.prepare_combo_df.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        temp_df = pd.concat( [ self.deep_1, self.deep_2, self.deep_3], sort=False, ignore_index=True ).sort_values(by=['Pct_change', 'M_B', 'Mkt_cap'], ascending=False, na_position='last')
        temp_df.reset_index(inplace=True, drop=True)                               # reset index each time so its guaranteed sequential
        self.combo_df = temp_df.sort_values(by=['Pct_change'], ascending=False )   # ensure sorted combo DF is avail as class global attr
        self.combo_dupes = self.combo_df.duplicated(['Symbol']).to_frame()         # convert Bool SERIES > DF & make avail as class global attr DF
        return

###################################################################################
# method 1

    def polish_combo_df(self, me):
        """
        Clean, Polish & Wax the main Combo DataFrame.
        We do a lot of heavy DF data generation/manipulation/insertion here.
        Fill-out key collumn data thats missing, incomplete and/or not reliable due to errors in initial data extraction
        """
        cmi_debug = __name__+"::"+self.polish_combo_df.__name__+".#"+str(self.inst_uid)+"."+str(me)
        logging.info( f"%s - CALLED" % cmi_debug )

        self.prepare_combo_df()                         # FIRST, merge Small_cap + med + large + mega into a single DF

        # Look into the main combo_df at the Unsual Vol columns
        # Find/fix missing data in nasdaq.com unusual volume DF - i.e. market_cap info
        #self.tag_dupes()
        #print ( f"{self.combo_dupes_only_listall(2)}" )
        
        uvol_badata = self.combo_df[self.combo_df['Mkt_cap'].isna()]   # Non and NaN = True
        uvol_badsymbols = uvol_badata['Symbol'].tolist()               # make list of bad symbols from the DF
        nq = nquote(4, self.args)                                      # setup an nasdaq.com quote instance to get live data from
        nq.init_dummy_session()                                        # nasdaq.com session setup
        self.total_wrangle_errors = 0
        self.unfixable_errors = 0
        self.cleansed_errors = 0
        self.wrangle_errors = 0
        self.loop_count = 1
        self.fixchars = 0
        self.cols = 1

        ############################### get quote Setup #################################
        # Get missing data from nasdaq.com. Rewrite in into combo_df.
        # This is network expensive - do a live network quote get for each stock
        logging.info( f"%s  - Get quote data from nasdaq.com for:  {len(uvol_badsymbols)} symbols" % cmi_debug )
        print ( f"========== ask nasdaq.com for missing quote data =====================================================" )
        for qsymbol in uvol_badsymbols:
            xsymbol = qsymbol
            qsymbol = qsymbol.rstrip()                   # cleand/striped of trailing spaces
            logging.info( f"%s  - get quote:  {qsymbol} : {self.loop_count}" % cmi_debug )
            nq.update_headers(qsymbol, "stocks")         # nasdaq.com session - set path: header object
            nq.form_api_endpoint(qsymbol, "stocks")      # nasdaq.com set API endpoint - default GUESS asset_class=stocks
            ac = nq.learn_aclass(qsymbol)                # nasdaq.com lead what the real asset class is

            if ac != "stocks":
                logging.info( f"%s  - re-shape asset class endpoint to: {ac}" % cmi_debug )
                nq.form_api_endpoint(qsymbol, ac)        # re-form API endpoint if default asset_class guess was wrong
                nq.get_nquote(qsymbol.upper())          # get a live quote
                wq = nq_wrangler(4, self.args)           # instantiate a class for Quote Data Wrangeling
                wq.asset_class = ac
                wq.setup_zones(4, nq.quote_json1, nq.quote_json2, nq.quote_json3)
                wq.do_wrangle()
                wq.clean_cast()
                wq.build_data_sets() 
                print ( f"{qsymbol:5}...", end="", flush=True )         # >> pretty printer <<
            else:
                nq.get_nquote(qsymbol.upper())           # get a live quote
                wq = nq_wrangler(3, self.args)           # instantiate a class for Quote Data Wrangeling
                wq.asset_class = ac
                wq.setup_zones(3, nq.quote_json1, nq.quote_json2, nq.quote_json3)
                wq.do_wrangle()
                wq.clean_cast()
                wq.build_data_sets()     
                print ( f"{qsymbol:5}...", end="", flush=True )         # >> pretty printer <<
            
        ############################### Phase 1 ###########################################
        # Evaluate Asset Class = an Exchnage Traded Fund (ETF)
            logging.info( f"{cmi_debug} - Begin market cap/scale logic cycle... {nq.asset_class}")
            if wq.asset_class == "etf":                                 # Global attribute - Cant get STOCK-type data for 'etf'
                logging.info( f"{cmi_debug} - {qsymbol} asset class is ETF" )
                self.wrangle_errors += 1
                self.unfixable_errors += 1
                print ( f"E!", end="" )                                 # >> pretty printer <<
                self.fixchars += 2
                z_float = round(float(0), 2)
                if self.args['bool_xray'] is True:
                    print ( f"=xray=========================== {self.inst_uid} ================================begin=" )
                    print ( f"z_float: {z_float}" )
                    print ( f"combo_df: {self.combo_df}" )
                    print ( f"=xray=========================== {self.inst_uid} ==================================end=" )

                row_index = self.combo_df.loc[self.combo_df['Symbol'] == xsymbol].index[0]
                self.combo_df.at[row_index, 'Mkt_cap'] = z_float      # set Market cap to 0 for ETF
                row_index = self.combo_df.loc[self.combo_df['Symbol'] == xsymbol].index[0]
                self.combo_df.at[row_index, 'M_B'] = 'EF'
            else:
                logging.info( f"{cmi_debug} - {qsymbol} asset class is {wq.asset_class}" )
                pass

        ############################### Phase 2 ###########################################
        # Evaluate Market Cap data field - quality of data
            logging.info( f"{cmi_debug} - Test {wq.asset_class} Mkt_cap for BAD data..." )
            z_float = round(float(0), 3)                  # 0.000
            try:
                null_tester = wq.qd_quote['mkt_cap']                    # some ETF/Funds have a market cap - but data is inconsistent
            except TypeError:
                logging.info( f"{cmi_debug} - {wq.asset_class} Mkt_cap data is NULL / setting to: 0" )
                if self.args['bool_xray'] is True:
                    print ( f"=xray=TypeError================= {self.inst_uid} ================================begin=" )
                    print ( f"quote: {wq.qd_quote.items()}" )
                    print ( f"combo_df: {self.combo_df}" )
                    print ( f"=xray=========================== {self.inst_uid} ==================================end=" )
                self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = 'UZ'    # make is a real number = 0
                print ( f"^^", end="" )                                 # >> pretty printer <<
                self.cleansed_errors += 2
                self.fixchars += 2
                y = 0
            except KeyError:
                logging.info( f"{cmi_debug} - {wq.asset_class} Mkt_cap key is NULL / setting to: 0" )
                if self.args['bool_xray'] is True:
                    print ( f"=xray=KeyError================== {self.inst_uid} ================================begin=" )
                    print ( f"quote: {wq.qd_quote.items()}" )
                    print ( f"combo_df: {self.combo_df}" )
                    print ( f"=xray=========================== {self.inst_uid} ==================================end=" )
                self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = 'UZ'    # make is a real number = 0 
                self.cleansed_errors += 1
                print ( f"!", end="" )                                  # >> pretty printer <<
                self.fixchars += 1
                y = 0
            else:
                logging.info( f"{cmi_debug} - Set {wq.asset_class} Mkt_cap to: {wq.qd_quote['mkt_cap']}" )
                z_float = (float(wq.qd_quote['mkt_cap']))                
                row_index = self.combo_df.loc[self.combo_df['Symbol'] == xsymbol].index[0]
                self.combo_df.at[row_index, 'Mkt_cap'] = round(z_float, 3)      # set Market cap to real/live num from nasdaq.com
                print ( f"$", end="" )                                  # >> pretty printer <<
                self.fixchars += 1
                self.cleansed_errors += 1

        ############################### Phase 3 ###########################################
        # Set the Market Cap scale tag (M_B col)
                if wq.asset_class == "stocks":
                    logging.info( f"{cmi_debug} - Compute Mkt_cap scale tag: [ {wq.qd_quote['mkt_cap']} ]..." )
                    for i in (("MT", 999999), ("LB", 10000), ("SB", 2000), ("LM", 500), ("SM", 50), ("TM", 10), ("UZ", 0)):
                        if wq.qd_quote['mkt_cap'] == float(0):
                            row_index = self.combo_df.loc[self.combo_df['Symbol'] == xsymbol].index[0]
                            self.combo_df.at[row_index, 'M_B'] = "UZ"
                            logging.info( f"{cmi_debug} - Bad Market cap: [ {wq.qd_quote['mkt_cap']} ] scale set to: UZ" )
                            print ( f"0", end="" )
                            self.fixchars += 1
                            break
                        elif i[1] >= wq.qd_quote['mkt_cap']:
                            pass
                        else:
                            row_index = self.combo_df.loc[self.combo_df['Symbol'] == xsymbol].index[0]
                            self.combo_df.at[row_index, 'M_B'] = i[0]
                            logging.info( f"{cmi_debug} - Market cap: [ {wq.qd_quote['mkt_cap']} ] scale set to: {i[0]}" )
                            self.wrangle_errors += 1          # insert market cap scale into DF @ column M_B for this symbol
                            self.cleansed_errors += 1
                            print ( f"+", end="" )
                            self.fixchars += 1
                            break
            # nice column/rows status bar to show the hard work we are grinding on...
            finally:
                if self.fixchars == 1: print ( f"   ", end="" )
                if self.fixchars == 2: print ( f"  ", end="" )
                if self.fixchars == 3: print ( f" ", end="" )
                self.fixchars = 0
                self.cols += 1
                if self.cols == 8:       # 8 symbols per row
                    print ( f" " )  # onlhy print 8 symbols per row
                    self.cols = 1
                else:
                    print ( f"/ ", end="" )

            logging.info( f"{cmi_debug} ================ end quote: {qsymbol} : {self.loop_count} ====================" )
            self.total_wrangle_errors = self.total_wrangle_errors + self.wrangle_errors
            self.wrangle_errors = 0
            self.loop_count += 1

        print ( " " )
        print ( " " )
        print  ( f"Symbols scanned: {self.loop_count-1} / Issues: {self.cleansed_errors} / Repaired: {self.total_wrangle_errors} / Unfixbale: {self.unfixable_errors}" )

        return
    
#############################################################################
# method #2

    def tag_dupes(self):
        """
        Find & Tag the *duplicate* entries in the combo_df matrix dataset, which is important b/c dupes
        here means these stocks are HOT and appearing across multiple dataframes.
        """
        cmi_debug = __name__+"::"+self.tag_dupes.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        self.combo_df = self.combo_df.assign(Hot="", Insights="" )     # pre-insert 2 new columns
        self.mpt = ()            # Helper: Internal DICT(tuple) element to find cheapest ***HOT stock

        for ds in self.combo_df[self.combo_df.duplicated(['Symbol'])].Symbol.values:    # ONLY work on dupes in DF !!!
            for row_idx in iter( self.combo_df.loc[self.combo_df['Symbol'] == ds ].index ):
                sym = self.combo_df.loc[row_idx].Symbol
                cap = self.combo_df.loc[row_idx].Mkt_cap
                scale = self.combo_df.loc[row_idx].M_B
                price = self.combo_df.loc[row_idx].Cur_price
                if pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == False and pd.isna(self.combo_df.loc[row_idx].M_B) == False:
                    self.combo_df.loc[row_idx,'Hot'] = "*Hot*"      # Tag as a **HOT** stock
                    self.combo_df.loc[row_idx,'Insights'] = self.cx.get(scale) + " + ^Un vol"     # Annotate why...
                    self.mpt = ( row_idx, sym.rstrip(), round(float(price), 2) )   # pack a tuple - for min_price analysis later
                    self.min_price.update({row_idx: self.mpt})           # load helpder DICT e.g. {1: (7, 'IBM', 120.51), 7: (24, 'TSLA', 138.21)}
                elif pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == True and pd.isna(self.combo_df.loc[row_idx].M_B) == True:
                     self.combo_df.drop([row_idx], inplace=True)    # drop this row from DF
                else:
                    print ( f"WARNING: Don't know what to do for: {sym} - Mkt_cap: {cap} / M_B: {scale}" )
                    break
            return

#####################################################################################
# method #2.1
# find and tag the lowest priced stock within the list of Hottest stocks
# must call tag_dupes() first as that tags hottest with *Hot* / this method relies on that

    def find_hottest(self):
        print ( f"\n========== Hot stock analysis ====================================================" )
        if self.min_price:                       # not empty, We have some **HOT stocks to evaluate
            print ( f"\nLocating...", end="" ) 
            mptv = min(( td[2] for td in self.min_price.values() )) # td[2] = iterator of 3rd elment of min_price{}
            for v in self.min_price.values():                       # v = tuple structured like: (0, IBM, 28.42)
                if v[2] == mptv:                                    # v[2] = 3rd element = price symbol
                    row_idx = int(v[0])                             # v[0] = 1st emelent = DF index of symbol
                    self.rx = [row_idx, v[1].rstrip()]              # add hottest stock with lowest price / 1 entry in list[]
                    self.combo_df.loc[row_idx,'Hot'] = "*Hot*"      # Tag as a **HOT** stock in DataFrame
                    found_sym = self.combo_df.loc[row_idx, 'Symbol']
                    print ( f" [ {found_sym.rstrip()} ] @ #{row_idx}" )
                    print ( f"========== complete ==============================================================" )
                    break
                else:
                    print ( f".", end="" )

        # TODO: ** This logic can fail @ Market open when many things are empty & unpopulated...
        if not bool(self.min_price):                # is empty?
            print ( f"NO **HOT tagged stocks located yet" )  

        return

#####################################################################################
# method #3

    def tag_uniques(self):
        """
        Find & Tag unique untagged entries in the combo_df dataset.
        ONLY do this after the tag_dupes, because its cleaner to eliminate & tage dupes first
        When you get to this phase, combo_df should now contain UNQIUES only
        """
        cmi_debug = __name__+"::"+self.tag_uniques.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )

        for row_idx in self.combo_df.loc[self.combo_df['Insights'] == "" ].index:
            logging.info('%s - Cycle over list of symbols' % cmi_debug )
            sym = self.combo_df.loc[row_idx].Symbol
            cap = self.combo_df.loc[row_idx].Mkt_cap
            scale = self.combo_df.loc[row_idx].M_B

            if pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == False and pd.isna(self.combo_df.loc[row_idx].M_B) == False:
                self.combo_df.loc[row_idx,'Insights'] = self.cx.get(scale)
            elif pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == True and pd.isna(self.combo_df.loc[row_idx].M_B) == True:
                logging.info('%s - Apply NaN/NaN inferrence logic' % cmi_debug )
                self.combo_df.loc[row_idx,'Insights'] = "^ Un vol only"
            else:
                logging.info('%s - Unknown logic discovered' % cmi_debug )
                self.combo_df.loc[row_idx,'Insights'] = "!No logic!"
        logging.info('%s - Exit tag uniques cycle' % cmi_debug )
        return

#################################################################################
# method 4
# a safety catch-all to scan for any NaaN's lying arround that wern't caught

    def tag_naans(self):
        """
        Hunt down and loose NaaN entries left lying arround
        """

        cmi_debug = __name__+"::"+self.tag_naans.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        print ( f"{self.combo_df[self.combo_df.isna().any(axis=1)]}" )
        return

        """
        for row_idx in self.combo_df.loc[self.combo_df['Insights'] == "" ].index:
            logging.info('%s - Cycle over list of symbols' % cmi_debug )
            sym = self.combo_df.loc[row_idx].Symbol
            cap = self.combo_df.loc[row_idx].Mkt_cap
            scale = self.combo_df.loc[row_idx].M_B

            if pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == False and pd.isna(self.combo_df.loc[row_idx].M_B) == False:
                self.combo_df.loc[row_idx,'Insights'] = self.cx.get(scale)
                #
            elif pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == True and pd.isna(self.combo_df.loc[row_idx].M_B) == True:
                self.combo_df.loc[row_idx].Mkt_cap = 0
                self.combo_df.loc[row_idx].M_B = 'UZ'
                logging.info('%s - Apply NaN/NaN inferrence logic' % cmi_debug )
                self.combo_df.loc[row_idx,'Insights'] = "^ Unusual vol only"
            else:
                logging.info('%s - Unknown logic discovered' % cmi_debug )
                self.combo_df.loc[row_idx,'Insights'] = "!No logic!"
        logging.info('%s - Exit tag uniques cycle' % cmi_debug )
        """

############################################################################
# method 5 Hottest 

    def rank_hot(self):
        """
        isolate all *Hot* tagged stocks and rank them by price, lowest=1 to highest=n
        Since these stocks are the most active all-round, tag_rank them with 1xx (e.g., 100, 101, 102, 103)
        """
        cmi_debug = __name__+"::"+self.rank_hot.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        self.combo_df = self.combo_df.assign(rank="" )     # pre-insert the new Tag_Rank column

        # get a list of rows that meet the critera and find each row's index ID's.
        # Pack the list of index ID's into a list [] & pass it as an indexer inside a Loop
        # use rank column to hold a tag/ranking of cheapest *Hot* stock to most expensive *Hot* stock
        #rh_df0 = self.combo_df.sort_values(by=['Cur_price'], ascending=True)
        #rh_list = rh_df0.loc[self.combo_df['Hot'] == "*Hot*"]

        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['Hot'] == "*Hot*"].index)
        y = 100                                  # HOT stocks ranking starts at 100
        for i in z:                              # cycle thru the sorted DF
            self.combo_df.loc[i, 'rank'] = y     # rank each Hot entry
            # DEBUG: print ( "i: ", i, "x:", y )
            y += 1
        return self.combo_df

###################################################################################
# method 6

    def rank_unvol(self):
        """
        Isolate all Unusual Vol stocks only.
        tag_rank them with code: 3xx (e.g. 300, 301, 302)
        """
        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['Insights'] == "^ Un vol only"].index)
        y = 300                                  # Unusual Vol stocks ranking starts at 300 
        for i in z:                              # cycle thru the sorted DF
            self.combo_df.loc[i, 'rank'] = y     # rank each Unique entry
            # DEBUG: print ( "i: ", i, "x:", y )
            y += 1
        return self.combo_df

###################################################################################
# method 7

    def rank_caps(self):
        """
        isolate any stock NOT tagged (i.e not Hot or Unusual Vol tagged).
        tag_rank them with code: 2xx (e.g. 200, 201, 202, 203)
        WARNING:
            This is a cheap way to find/select criteria.
            MUST call this ranking method last for this to work correctly.
        """
        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['rank'] == "" ].index)
        y = 200                                 # Non tagged average unknown stocks ranking starts at 200
        for i in z:                             # cycle thru the sorted DF
            self.combo_df.loc[i, 'rank'] = y    # rank each entry
            # DEBUG : print ( "i: ", i, "x:", y )
            y += 1
        return self.combo_df

###################################################################################
# method 8

    def combo_listall(self):
        """
        Print the full contents of the combo DataFrame. All comumns. Not sorted.
        WARNING:
        DF contains DUPLICATE rows b/c **Hot** stocks appear multiple times.
        """
        cmi_debug = __name__+"::"+self.combo_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        return self.combo_df

###################################################################################
# method 9

    def combo_listall_ranked(self):
        """
        Print the full contents of the combo DataFrame. Sorted by % Change
        WARNING:
        DF contains DUPLICATE rows b/c **Hot** stocks appear multiple times.
        """
        cmi_debug = __name__+"::"+self.combo_listall_ranked.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        # DEBUG: print ( self.combo_df.sort_values(by=['Pct_change'], ascending=False) )
        return self.combo_df.sort_values(by=['Pct_change'], ascending=False)

###################################################################################
# method 10

    def combo_listall_nodupes(self):
        """
        Print the entire combo DataFrame.
        DUPES REMOVED. Sorted by % Change
        """
        cmi_debug = __name__+"::"+self.combo_listall_nodupes.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        c = self.combo_df.drop_duplicates(subset=['Symbol'], keep='first')    # only look at dupes in symbol colum
        # return c.sort_values(by=['Pct_change'], ascending=False)
        return c    #  raw df list. DO NOT sort by anything

###################################################################################
# method 11

    def list_uniques(self):
        """
        Print the full contents of the combo DataFrame with DUPES removed
        NOT sorted
        note: method can be deleted. It is replcaed by unique_symbols
        """
        cmi_debug = __name__+"::"+self.list_uniques.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        return self.combo_df.drop_duplicates(subset=['Symbol'], keep='first')    # only look at dupes in symbol colum

###################################################################################
# method 12

    def unique_symbols(self):
        """
        Build a DF of UNIQUE symbols from the combo DataFrame with DUPES remove
        (keep the FIRST instance of each dupe discovered. Sort by Symbol
        """
        cmi_debug = __name__+"::"+self.unique_symbols.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        unique_s = self.combo_df.drop_duplicates(subset=['Symbol'], keep='first')     # only look at dupes in symbol colum
        return unique_s.sort_values(by=['Symbol'])

###################################################################################
# method 13

    def combo_grouped(self, opt):
        """
        Print a set of insights like Agerages and Mean etc
        Sorted by % Change & grouped by Insights
        """
        cmi_debug = __name__+"::"+self.combo_grouped.__name__+".#"+str(self.inst_uid)
        self.gopt = opt
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)

        if self.gopt == 1:   # pct grouping
            g_df = pd.DataFrame(self.combo_df.sort_values(by=['rank'], ascending=True).groupby(['Insights'])['Pct_change'].mean() )
        
        if self.gopt == 2:   # prc grouping
            g_df = pd.DataFrame(self.combo_df.sort_values(by=['rank'], ascending=True).groupby(['Insights'])['Prc_change'].mean() )
        
        #g_df = pd.DataFrame(self.combo_df.sort_values(by=['rank'], ascending=True).groupby(['Insights']) )
        
        g_df.loc['Average_overall'] = g_df.mean()
        
        return g_df

###################################################################################
# method 14

    def combo_dupes_only_listall(self, opt):
        """
        returns ad DF
        Print the full contents of the combo DataFrame with the DUPES tagged & sorted by % Change.
        Will only list the dupes unless you have called tag_dupes() first, and then youll get the full DF
        """
        cmi_debug = __name__+"::"+self.combo_dupes_only_listall.__name__+".#"+str(self.inst_uid)
        self.opt = opt
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)

        if self.opt == 1:
            # dupe symbols show up b/c they are very active & all over the data. They are tagged as HOT stocks
            temp_1 = self.combo_df.sort_values(by=['Pct_change'], ascending=False)
            return (temp_1[temp_1.duplicated(['Symbol'])] )

        if self.opt == 2:
            return ( self.combo_dupes[self.combo_dupes[0] == True] )

        return

###################################################################################
# method 15

    def reindex_combo_df(self):
        """
        Make combo_df index numbering linear; starting from 0, 1, 2, 3, 4...
        WANRING:
        This will write the new index INTO the exiting combo DF. Its a permenant change.
        Only do this if you are very sure you must do this NOW...!
        """
        cmi_debug = __name__+"::"+self.reindex_combo_df.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        self.combo_df.reset_index(inplace=True, drop=True)                         # reset index each time so its guaranteed sequential
        return
