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
        deep_1 = self.dataset_1.tg_df1.drop(columns=[ 'ERank', 'Time' ]).sort_values(by='Pct_change', ascending=False )
        deep_2 = self.dataset_2.dg1_df1.drop(columns=[ 'Row', 'Time' ] )
        deep_3 = self.dataset_3.up_df0.drop(columns=[ 'Row', 'Time', 'Vol', 'Vol_pct']).sort_values(by='Pct_change', ascending=False )

        # combine all dataframes...
        combo_df = pd.concat( [ deep_1, deep_2, deep_3], sort=False, ignore_index=True ).sort_values(by=['Pct_change', 'M_B', 'Mkt_cap'], ascending=False, na_position='last')
        combo_df.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential

        deep_5 = combo_df.sort_values(by=['Pct_change'], ascending=False )    # prepare a sorted df
        combo_dupes = deep_5.duplicated(['Symbol']).to_frame()                # pd.duplicated outputs a SERIES

        print ( "========== DEEP combo no dupes : outlyers described ==========================================" )
        combo_df.drop( combo_dupes[combo_dupes[0] == True].index, inplace=True )        # permenantly on the original df
        combo_df = combo_df.assign(Entropy="" )

        for x in deep_5[deep_5.duplicated(['Symbol'])].Symbol.values:
            row_idx = int(combo_df.loc[combo_df['Symbol'] == x ].index.values)
            cap_size = combo_df.loc[combo_df['Symbol'] == x ].M_B.values
            if cap_size == 'M':
                cap_size = '*Small cap*'
            else:
                cap_size = 'Large cap'
            combo_df.loc[row_idx,'Entropy'] = "Unusual vol "+cap_size

        #print ( combo_df )
        self.combo_df = combo_df    # ensure DataFrame is class global attribute
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
    def combo_listall(self):
        """Print the full contents of the combo DataFrame"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.combo_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.combo_df.sort_values(by='Pct_change', ascending=False ) )
        return
