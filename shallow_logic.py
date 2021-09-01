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

#####################################################

class shallow_combo:
    """Class to do deeper logic thinking across multiple dataframes"""
    """Although this is not considerd DEEP Logic, Machine Learning, or Ai logic."""
    dataset_1 = ""
    dataset_2 = ""
    dataset_3 = ""
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
        'TM': 'Tiny cap + % gainer',
        }

    def __init__(self, i, d1, d2, d3, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        self.args = global_args
        self.dataset_1 = d1     # med_large_mega_gainers inst -> y_topgainers.tg_df1
        self.dataset_2 = d2     # small_cap_gainers inst -> screener_dg1.dg1_df1
        self.dataset_3 = d3     # unusual_vol_activity inst -> unusual_vol.up_df0
        self.inst_uid = i

    def __repr__(self):
        return ( f'{self.__class__.__name__}(' f'{self.inst_uid!r})' )

# method #1
    def prepare_combo_df(self):
        cmi_debug = __name__+"::"+self.prepare_combo_df.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        deep_1 = self.dataset_1.tg_df1.drop(columns=[ 'ERank', 'Time' ]).sort_values(by='Pct_change', ascending=False )
        deep_2 = self.dataset_2.dg1_df1.drop(columns=[ 'Row', 'Time' ] )
        deep_3 = self.dataset_3.up_df0.drop(columns=[ 'Row', 'Time', 'Vol', 'Vol_pct']).sort_values(by='Pct_change', ascending=False )

        # combine all dataframes...
        # prescribed concoluted Pandas logic b/c problematic & error-prone when done as a pandas 1-liner
        temp_df = pd.concat( [ deep_1, deep_2, deep_3], sort=False, ignore_index=True ).sort_values(by=['Pct_change', 'M_B', 'Mkt_cap'], ascending=False, na_position='last')
        temp_df.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential

        #deep_5 = temp_df.sort_values(by=['Pct_change'], ascending=False )    # prepare a sorted df
        #combo_dupes = deep_5.duplicated(['Symbol']).to_frame()                # pd.duplicated outputs a SERIES
        self.combo_df = temp_df.sort_values(by=['Pct_change'], ascending=False )   # ensure sorted combo DF is avail as class global attr
        self.combo_dupes = self.combo_df.duplicated(['Symbol']).to_frame()         # convert Bool SERIES > DF & make avail as class global attr DF
        return

        # possible logic...
        # scan Nan rows DataFrame
        # does each item in duplicates DataFrame exists in NaN DataFrame - !!! also need symbol here
            # YES = guaranteed to have originated from Unusual List table_section
            # NO = bad data0 maybe?
        # on YES...
            # scan full deep combo DataFrame
            # drop row identified dupe row from deep combo DataFrame
            # search deep combo DataFrame (by symbol) of dupe item
                # add column info == "Unusual volume by xxx%"
                # add colum info == "Small, medium. large, mega - cap company"

# method #2
    def tag_dupes(self):
        """Find & Tag the *duplicate* entries in the combo matrix dataset."""
        """This is important b/c dupes mean these stocks are HOT and appearing in multiple dataframes."""

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
                    #np.array2string(np.char.ljust(self.cx.get(scale), 20) )
                    #annotation = "+ % gainer " + self.cx.get(scale)
                    #self.combo_df.loc[row_idx,'Insights'] = annotation.lstrip()     # Annotate why...
                    mpt = ( row_idx, sym, price )     # pack a tuple - for min_price analysis later
                    min_price.update({row_idx: mpt})
                elif pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == True and pd.isna(self.combo_df.loc[row_idx].M_B) == True:
                    self.combo_df.drop([row_idx], inplace=True)
                else:
                    Print ( "WARNING: Don't know what to do !!" )

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
        """Find & Tag unique untagged entries in the combo matrix dataset."""
        """ONLY do this after the tag_dupes, because its cleaner to eliminate & tage dupes first"""
        """When you get to this, the entire dataframe should now contain UNQIUES only"""

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
        logging.info('%s - Exit tagging cycle' % cmi_debug )
        return

    def rank_hot(self):
        """isolate all *Hot* tagged stocks and rank them by price, lowest=1 to highest=n."""
        """Since these stocks are the most active all-round, tag_rank them with 1xx (e.g., 100, 101, 102, 103)"""

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
        """Isolate all Unusual Vol stocks only, and tag_rank them with 3xx (e.g. 300, 301, 302)"""

        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['Insights'] == "^ Unusual vol only"].index)
        y = 300
        for i in z:
            self.combo_df.loc[i, 'rank'] = y
            #print ( "i: ", i, "x:", y )
            y += 1
        return self.combo_df

    def rank_caps(self):
        """isolate all non-*Hot* stocks and all non-Unusual Vol stocks, and tag_rank them  with 2xx (e.g. 200, 201, 202, 203)"""
        """WARN: This is a cheap way to find/select criteria. MUST call this ranking method last for this to work correctly."""
        z = list(self.combo_df.sort_values(by=['Cur_price'], ascending=True).loc[self.combo_df['rank'] == "" ].index)
        y = 200
        for i in z:
            self.combo_df.loc[i, 'rank'] = y
            #print ( "i: ", i, "x:", y )
            y += 1
        return self.combo_df


    def combo_listall(self):
        """Print the full contents of the combo DataFrame with DUPES"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.combo_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        return self.combo_df

    def combo_listall_ranked(self):
        """Print the full contents of the combo DataFrame with DUPES"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.combo_listall_ranked.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        print ( self.combo_df.sort_values(by=['Pct_change'], ascending=False) )
        return

    def combo_grouped(self):
        """Print a set of insights like Agerages and Mean etc"""
        """Sorted by % Change & grouped by Insights"""

        cmi_debug = __name__+"::"+self.combo_grouped.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        g_df = pd.DataFrame(self.combo_df.sort_values(by=['rank'], ascending=True).groupby(['Insights'])['Pct_change'].mean() )
        g_df.loc['Average_overall'] = g_df.mean()
        return g_df

    def combo_dupes_only_listall(self, opt):
        """Print the full contents of the combo DataFrame with the DUPES tagged & sorted by % Change.
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
