#!/usr/bin/python3
import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
import threading

# logging setup
logging.basicConfig(level=logging.INFO)

# my private classes & methods
from nasdaq_uvoljs import un_volumes
from nasdaq_quotes import nquote
from bigcharts_md import bc_quote
from marketwatch_md import mw_quote
from y_techevents import y_techevents

#####################################################

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
    args = []           # class dict to hold global args being passed in from main() methods
    rx = []             # hottest stock with lowest price overall
    cx = { 'LT': 'Mega cap + % gainer only', \
        'LB': 'Large cap + % gainer only', \
        'LM': 'Med cap + % gainer only', \
        'LZ': 'Zero Large cap + % gainer only', \
        'SB': 'Big Small cap + % gainer only', \
        'SM': 'Small cap + % gainer only', \
        'SZ': 'Zero Small cap + % gainer only', \
        'EF': 'ETF Fund Trust + % gainer only', \
        'UZ': 'Unknown cap + % gainer only', \
        'TM': 'Tiny cap + % gainer',
        }

    def __init__(self, i, d1, d2, d3, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        self.args = global_args
        self.deep_1 = d1.tg_df1.drop(columns=[ 'ERank', 'Time' ]).sort_values(by='Pct_change', ascending=False )
        self.deep_2 = d2.dg1_df1.drop(columns=[ 'Row', 'Time' ] )
        self.deep_3 = d3.up_df0.drop(columns=[ 'Row', 'Time', 'Vol', 'Vol_pct']).sort_values(by='Pct_change', ascending=False )
        self.inst_uid = i
        return

    def __repr__(self):
        return ( f'{self.__class__.__name__}(' f'{self.inst_uid!r})' )

# method #1
    def prepare_combo_df(self):
        """
        combo_df will become the Single Source of Truth dataset.
        """
        cmi_debug = __name__+"::"+self.prepare_combo_df.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        temp_df = pd.concat( [ self.deep_1, self.deep_2, self.deep_3], sort=False, ignore_index=True ).sort_values(by=['Pct_change', 'M_B', 'Mkt_cap'], ascending=False, na_position='last')
        temp_df.reset_index(inplace=True, drop=True)                               # reset index each time so its guaranteed sequential
        self.combo_df = temp_df.sort_values(by=['Pct_change'], ascending=False )   # ensure sorted combo DF is avail as class global attr
        self.combo_dupes = self.combo_df.duplicated(['Symbol']).to_frame()         # convert Bool SERIES > DF & make avail as class global attr DF
        return

# method #2
    def tag_dupes(self):
        """
        Find & Tag the *duplicate* entries in the combo_df matrix dataset, which is important b/c dupes
        here means these stocks are HOT and appearing across multiple dataframes.
        """
        cmi_debug = __name__+"::"+self.tag_dupes.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        self.combo_df = self.combo_df.assign(Hot="", Insights="" )     # pre-insert 2 new columns
        min_price = {}      # Heler: DICT to help find cheapest ***HOT stock
        mpt = ()            # Helper: Internal DICT(tuple) element to find cheapest ***HOT stock
        for ds in self.combo_df[self.combo_df.duplicated(['Symbol'])].Symbol.values:    # ONLY work on dupes in DF !!!
            for row_idx in iter( self.combo_df.loc[self.combo_df['Symbol'] == ds ].index ):
                sym = self.combo_df.loc[row_idx].Symbol
                cap = self.combo_df.loc[row_idx].Mkt_cap
                scale = self.combo_df.loc[row_idx].M_B
                price = self.combo_df.loc[row_idx].Cur_price
                if pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == False and pd.isna(self.combo_df.loc[row_idx].M_B) == False:
                    self.combo_df.loc[row_idx,'Hot'] = "*Hot*"      # Tag as a **HOT** stock
                    self.combo_df.loc[row_idx,'Insights'] = self.cx.get(scale) + " + Unu vol"     # Annotate why...
                    mpt = ( row_idx, sym, price )     # pack a tuple - for min_price analysis later
                    min_price.update({row_idx: mpt})
                elif pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == True and pd.isna(self.combo_df.loc[row_idx].M_B) == True:
                     self.combo_df.drop([row_idx], inplace=True)
                else:
                    print ( f"WARNING: Don't know what to do for: {sym} / Mkt_cap: {cap} / M_B: {scale}" )
                    break

        # TODO: ** This logix test is BUGGY & possible faills at Market open when many things are empty & unpopulated...
        if not bool(min_price):         # is empty?
            print ( "No **HOT stocks to evaluate yet" )

        # since we are Tagging and annotating this DataFrame...
        # find and tag the lowest priced stock within the list of Hottest stocks
        if min_price:     # We have some **HOT stocks to evaluate
            mptv = min(( td[2] for td in min_price.values() ))      # Output = 1 single value from a generator of tuples
            for v in min_price.values():    # v = tuple structured like: (0, BEAM, 28.42)
                if v[2] == mptv:            # v[2] = 3rd element = price for this stock symbol
                    row_idx = int(v[0])     # v[0] = 1st emelent = DataFrame index for this stock symbol
                    self.rx = [row_idx, v[1].rstrip()]      # add hottest stock with lowest price (will only ever be 1 entry in list[])
                    self.combo_df.loc[row_idx,'Hot'] = "*Hot*"      # Tag as a **HOT** stock in DataFrame

        return

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
                self.combo_df.loc[row_idx,'Insights'] = "^ Unusual vol only"
            else:
                logging.info('%s - Unknown logic discovered' % cmi_debug )
                self.combo_df.loc[row_idx,'Insights'] = "!No logic!"
        logging.info('%s - Exit tag uniques cycle' % cmi_debug )
        return

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
        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['Hot'] == "*Hot*"].index)
        y = 100
        for i in z:
            self.combo_df.loc[i, 'rank'] = y
            #print ( "i: ", i, "x:", y )
            y += 1

        return self.combo_df

    def rank_unvol(self):
        """
        Isolate all Unusual Vol stocks only, and tag_rank them with 3xx (e.g. 300, 301, 302)
        """

        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['Insights'] == "^ Unusual vol only"].index)
        y = 300
        for i in z:
            self.combo_df.loc[i, 'rank'] = y
            #print ( "i: ", i, "x:", y )
            y += 1
        return self.combo_df

    def rank_caps(self):
        """
        isolate all non-*Hot* stocks and all non-Unusual Vol stocks, and tag_rank them  with 2xx (e.g. 200, 201, 202, 203)
        WARN: This is a cheap way to find/select criteria. MUST call this ranking method last for this to work correctly.
        """

        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['rank'] == "" ].index)
        y = 200
        for i in z:
            self.combo_df.loc[i, 'rank'] = y
            #print ( "i: ", i, "x:", y )
            y += 1
        return self.combo_df


    def combo_listall(self):
        """
        Print the full contents of the combo DataFrame with DUPES
        Sorted by % Change
        """

        cmi_debug = __name__+"::"+self.combo_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        return self.combo_df

    def combo_listall_ranked(self):
        """
        Print the full contents of the combo DataFrame with DUPES
        Sorted by % Change
        """

        cmi_debug = __name__+"::"+self.combo_listall_ranked.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        #print ( self.combo_df.sort_values(by=['Pct_change'], ascending=False) )
        return self.combo_df.sort_values(by=['Pct_change'], ascending=False)

    def combo_grouped(self):
        """
        Print a set of insights like Agerages and Mean etc
        Sorted by % Change & grouped by Insights
        """

        cmi_debug = __name__+"::"+self.combo_grouped.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        #g_df = pd.DataFrame(self.combo_df.sort_values(by=['rank'], ascending=True).groupby(['Insights'])['Pct_change'].mean() )
        g_df = pd.DataFrame(self.combo_df.sort_values(by=['rank'], ascending=True).groupby(['Insights']).mean() )
        g_df.loc['Average_overall'] = g_df.mean()
        return g_df

    def combo_dupes_only_listall(self, opt):
        """
        Print the full contents of the combo DataFrame with the DUPES tagged & sorted by % Change.
        Will only list the dupes unless you have called tag_dupes() first, and then youll get the full DF
        """

        cmi_debug = __name__+"::"+self.combo_dupes_only_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)

        if opt == 1:
            temp_1 = self.combo_df.sort_values(by=['Pct_change'], ascending=False)
            return (temp_1[temp_1.duplicated(['Symbol'])] )

        if opt == 2:
            return ( self.combo_dupes[self.combo_dupes[0] == True] )

        return


    def polish_combo_df(self, me):
        """
        Clean, Polish & Wax the main Combo DataFrame. We do a lot of heavy DF data generation/manipulation/insertion
        Fill-out key collumn data that missing, incomplete and/or not reliable due to errors in initial data exttraction
        & collection process... becasue exchange data is not 100% reliable as we collect it in real time (surprisingly!)
        """

        cmi_debug = __name__+"::"+self.polish_combo_df.__name__+".#"+str(self.inst_uid)+"."+str(me)
        logging.info( f"{cmi_debug} - CALLED" )

        self.prepare_combo_df()      # FIRST, merge Small_cap + med + large + mega into a single DF

        # Find/fix missing data in nasdaq.com unusual volume DF - i.e. market_cap info
        uvol_badata = self.combo_df[self.combo_df['Mkt_cap'].isna()]
        up_symbols = uvol_badata['Symbol'].tolist()
        nq = nquote(3, self.args)                   # setup an nasdaq quote dict
        nq.init_dummy_session()                # setup request session - note: will set nasdaq magic cookie
        total_wrangle_errors = 0               # usefull counters
        unfixable_errors = 0
        cleansed_errors = 0
        logging.info( f"{cmi_debug} - find missing data for: {len(up_symbols)} symbols" )
        loop_count = 1
        print ( f"Collect & insert missing data elements [Nasdaq Unusual UP volume]..." )
        cols = 1
        fixchars = 0

        for qsymbol in up_symbols:
            xsymbol = qsymbol
            qsymbol = qsymbol.rstrip()                   # cleand/striped of trailing spaces
            logging.info( f"{cmi_debug} ================ get quote: {qsymbol} : {loop_count} ====================" )
            nq.update_headers(qsymbol, "stocks")         # set path: header object. doesnt touch secret nasdaq cookies
            nq.form_api_endpoint(qsymbol, "stocks")      # set API endpoint url - default GUESS asset_class=stocks
            ac = nq.learn_aclass(qsymbol)
            if ac != "stocks":
                logging.info( f"{cmi_debug} - re-shape asset class endpoint to: {ac}" )
                nq.form_api_endpoint(qsymbol, ac)      # re-form API endpoint if default asset_class guess was wrong)
            nq.get_nquote(qsymbol)                     # get a live quote
            wrangle_errors = nq.build_data()           # wrangle & cleanse the data - lots done in here

            print ( f"{qsymbol:5}...", end="", flush=True )
            logging.info( f"{cmi_debug} - Begin market cap/scale logic cycle... {nq.asset_class}")
            if nq.asset_class == "etf":        # Global attribute - is asset class ETF? yes = Cant get STOCK-type data
                logging.info( f"{cmi_debug} - {qsymbol} asset class is ETF" )
                wrangle_errors += 1
                unfixable_errors += 1     # set default data for non-regualr stocks
                print ( f"!!", end="" )
                fixchars += 2
                self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = round(float(0), 3)
                self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'M_B'] = 'EF'
            else:
                logging.info( f"{cmi_debug} - {qsymbol} asset class is {nq.asset_class}" )
                pass

            #
            logging.info( f"{cmi_debug} - Test {nq.asset_class} Mkt_cap for NULLs..." )
            try:
                null_tester = nq.quote['mkt_cap']         # some ETF/Funds have a market cap - but this state is inconsistent & random
            except TypeError:
                logging.info( f"{cmi_debug} - {nq.asset_class} Mkt_cap data is NULL / setting to: 0" )
                self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = round(float(0), 3)
                print ( f"!!", end="" )
                cleansed_errors += 2
                fixchars += 2
                y = 0
            except KeyError:
                logging.info( f"{cmi_debug} - {nq.asset_class} Mkt_cap key is NULL / setting to: 0" )
                self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = round(float(0), 3)
                cleansed_errors += 1
                print ( f"!", end="" )
                fixchars += 1
                y = 0
            else:
                logging.info( f"{cmi_debug} - Set {nq.asset_class} Mkt_cap to: {nq.quote['mkt_cap']}" )
                self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'Mkt_cap'] = nq.quote['mkt_cap']
                print ( f"+", end="" )
                fixchars += 1
                cleansed_errors += 1
                if nq.asset_class == "stocks":
                    logging.info( f"{cmi_debug} - Compute Mkt_cap scale tag: [ {nq.quote['mkt_cap']} ]..." )
                    for i in (("MT", 999999), ("LB", 10000), ("SB", 2000), ("LM", 500), ("SM", 50), ("TM", 10), ("UZ", 0)):
                        if nq.quote['mkt_cap'] == float(0):
                            self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'M_B'] = "UZ"
                            logging.info( f"{cmi_debug} - Bad Market cap: [ {nq.quote['mkt_cap']} ] / scale set to: UZ" )
                            print ( f"+", end="" )
                            fixchars += 1
                            break
                        elif i[1] >= nq.quote['mkt_cap']:
                            pass
                        else:
                            self.combo_df.at[self.combo_df[self.combo_df['Symbol'] == xsymbol].index, 'M_B'] = i[0]
                            logging.info( f"{cmi_debug} - Market cap: [ {nq.quote['mkt_cap']} ] scale set to: {i[0]}" )
                            wrangle_errors += 1          # insert market cap scale into DF @ column M_B for this symbol
                            cleansed_errors += 1
                            print ( f"+", end="" )
                            fixchars += 1
                            break
            # nice column/rows status bar to show the hard work we are grinding on...
            finally:
                if fixchars == 1: print ( f"   ", end="" )
                if fixchars == 2: print ( f"  ", end="" )
                if fixchars == 3: print ( f" ", end="" )
                cols += 1
                if cols == 8:       # 8 symbols per row
                    print ( f" " )  # onlhy print 8 symbols per row
                    cols = 1
                else:
                    print ( f"/ ", end="" )
                    fixchars = 0

            logging.info( f"{cmi_debug} ================ end quote: {qsymbol} : {loop_count} ====================" )
            total_wrangle_errors = total_wrangle_errors + wrangle_errors
            wrangle_errors = 0
            loop_count += 1

        print ( " " )
        print  ( f"Symbols scanned: {loop_count-1} / Issues: {cleansed_errors} / Repaired: {total_wrangle_errors} / Unfixbale: {unfixable_errors}" )

        return
