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
    args = []               # class dict to hold global args being passed in from main() methods

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

    def tag_dupes(self):
        """Find & Tag the *duplicate* entries in the combo matrix dataset."""
        """This is important b/c dupes mean these stocks are HOT and appearing in multiple dataframes."""

        cmi_debug = __name__+"::"+self.tag_dupes.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        self.combo_df = self.combo_df.assign(Hot="", Insights="" )     # pre-insert 2 new columns
        min_price = {}      # a tuple to help find cheapest ***HOT stock
        mpt = ()      # a tuple to help find cheapest ***HOT stock
        for ds in self.combo_df[self.combo_df.duplicated(['Symbol'])].Symbol.values:    # ONLY work on dupes in DF !!!
            for row_idx in iter( self.combo_df.loc[self.combo_df['Symbol'] == ds ].index ):
                sym = self.combo_df.loc[row_idx].Symbol
                cap = self.combo_df.loc[row_idx].Mkt_cap
                scale = self.combo_df.loc[row_idx].M_B
                price = self.combo_df.loc[row_idx].Cur_price
                if pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == False and pd.isna(self.combo_df.loc[row_idx].M_B) == False:
                    # Annotate in english why this stock is a ** Perosn of interest **
                    cx = { 'LT': '+ Mega cap + Unu vol', \
                        'LB': '+ Large cap + Unu vol', \
                        'LM': '+ Med cap + Unu vol', \
                        'LZ': '+ Zero Large cap + Unu vol', \
                        'SB': '+ Big Small cap + Unu vol', \
                        'SM': '+ Small cap + Unu vol', \
                        'SZ': '+ Zero Small cap + Unu vol',
                        }
                    self.combo_df.loc[row_idx,'Hot'] = "*Hot*"      # Tag as a **HOT** stock
                    self.combo_df.loc[row_idx,'Insights'] = "+ % gainer " + cx.get(scale)     # Annotate why...
                    mpt = ( row_idx, sym, price )     # pack a tuple - for min_price analysis later
                    min_price.update({row_idx: mpt})
                elif pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == True and pd.isna(self.combo_df.loc[row_idx].M_B) == True:
                    self.combo_df.drop([row_idx], inplace=True)
                else:
                    Print ( "Don't know what to do !!" )
        # since we are Tagging and annotating...
        # find and tage the lowest priced stock within the list of Hottest identified stocks
        mptv = min(( td[2] for td in min_price.values() ))      # Output = 1 single value from a generator of tuples
        for v in min_price.values():
            if v[2] == mptv:
                row_idx = int(v[0])
                print ( "Best price **Hottest stock:", v[1].rstrip(), "price:", v[2] )
                self.combo_df.loc[row_idx,'Hot'] = ">BEST<"      # Tag as a **HOT** stock
                #self.combo_df.set_value(row_idx, Hot, ">>Best<<")
        print ( " " )
        return

    def tag_uniques(self):
        """Find & Tag unique untagged entries in the combo matrix dataset."""
        """ONLY do this after the tag_dupes, because its cleaner to eliminate & tage dupes first"""
        """When you get to this, the entire dataframe should now contain UNQIUES only"""

        cmi_debug = __name__+"::"+self.tag_uniques.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )

        #for ds in self.combo_df[self.combo_df.duplicated(['Symbol'])].Symbol.values:    # ONLY work on dupes in DF !!!
        for row_idx in self.combo_df.loc[self.combo_df['Insights'] == "" ].index:
            logging.info('%s - Cycle over list of symbols' % cmi_debug )
            sym = self.combo_df.loc[row_idx].Symbol
            cap = self.combo_df.loc[row_idx].Mkt_cap
            scale = self.combo_df.loc[row_idx].M_B
            #print ( "Inex:", row_idx, "Symbol:", sym, "Mkt_cap:", cap, "Scale:", scale)
            if pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == False and pd.isna(self.combo_df.loc[row_idx].M_B) == False:
                logging.info('%s - Apply good data inferrence logic' % cmi_debug )
                # Annotate in english why this stock is a ** Perosn of interest **
                ## NaN + NaN = Unusually high volume, but nothing else
                # MKt_cap + M_B good data = Just a big day % gainer
                cx = { 'LT': 'Mega cap % gainer only', \
                    'LB': 'Large cap % gainer only', \
                    'LM': 'Med cap % gainer only', \
                    'LZ': 'Zero Large cap % gainer only', \
                    'SB': 'Big Small cap % gainer only', \
                    'SM': 'Small cap % gainer only', \
                    'SZ': 'Zero Small cap % gainer only',
                    }
                self.combo_df.loc[row_idx,'Insights'] = cx.get(scale)
                #print ( "Tagging row: ", "- Symbol: ", sym, "- Mkt Cap: ", cap, "- Scale: ", scale, "- Tag: ", cx.get(scale, 'Cap ERROR!') )
            elif pd.isna(self.combo_df.loc[row_idx].Mkt_cap) == True and pd.isna(self.combo_df.loc[row_idx].M_B) == True:
                logging.info('%s - Apply NaN/NaN inferrence logic' % cmi_debug )
                #print ( "Deleting row: ", "- Symbol: ", sym, "- Mkt Cap: ", cap, "- Scale: ", scale)
                self.combo_df.loc[row_idx,'Insights'] = "^ Unusual vol only"
            else:
                logging.info('%s - Unknown logic discovered' % cmi_debug )
                self.combo_df.loc[row_idx,'Insights'] = "!No logic!"
        logging.info('%s - Exit tagging cycle' % cmi_debug )
        return

    def tag_best_play(self):
        pass

# method #2
    def combo_listall(self):
        """Print the full contents of the combo DataFrame with DUPES"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.combo_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 40)
        return self.combo_df

# method #3
    def combo_dupes_only_listall(self, opt):
        """Print the full contents of the combo DataFrame"""
        """ with the DUPES tagged & sorted by % Change"""
        """Will only list the dupes unless you have called tag_dupes() first, and then youll get the full DF"""

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
