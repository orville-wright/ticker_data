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

    def __init__(self, i, d1, d2, d3):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INSTANTIATE' % cmi_debug )
        self.args = global_args
        self.dataset_1 = d1     # med_large_mega_gainers -> y_topgainers.tg_df1
        self.dataset_1 = d2     # small_cap_gainers -> screener_dg1.dg1_df1
        self.dataset_1 = d3     # unusual_vol_activity -> unusual_vol.up_df0
        self.inst_uid = i

    def __repr__(self):
        return ( f'{self.__class__.__name__}(' f'{self.inst_uid!r})' )

method #1
    def prepare_combo(self):
        deep_1 = self.dataset_1.tg_df1.drop(columns=[ 'ERank', 'Time' ]).sort_values(by='Pct_change', ascending=False )
        deep_2 = self.dataset_1.dg1_df1.drop(columns=[ 'Row', 'Time' ] )
        deep_3 = self.dataset_1.up_df0.drop(columns=[ 'Row', 'Time', 'Vol', 'Vol_pct']).sort_values(by='Pct_change', ascending=False )
        deep_4 = pd.concat( [ deep_1, deep_2, deep_3], sort=False, ignore_index=True ).sort_values(by=['Pct_change', 'M_B', 'Mkt_cap'], ascending=False, na_position='last')
        deep_4.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        # now scan unusual volume stocks for stock existing in the new combo DataFrame & tage them in a new column

        # print ( "========== Full DEEP combo DataFrame =====================================================" )
        # print ( deep_4 )
        # print ( "========== DEEP combo : duplicates only - style #1 =====================================================" )
        # deep_5 = deep_4.sort_values(by=['Pct_change'], ascending=False )[deep_4.duplicated(['Symbol'])]   # this works **KEEP**
        deep_5 = deep_4.sort_values(by=['Pct_change'], ascending=False )    # prepare a sorted df
        # print ( deep_5[deep_5.duplicated(['Symbol'])] )                     # full dataframe table
        # print ( deep_5[deep_5.duplicated(['Symbol'])].Symbol.values )       # just the symbols as list
        # print ( deep_5[deep_5.duplicated(['Symbol'])].index )               # index ID's as a list

        # print ( "========== DEEP combo : duplicates only - style #2 =====================================================" )
        deep_6 = deep_5.duplicated(['Symbol']).to_frame()      # pd.duplicated outputs a SERIES
        # print ( deep_6[deep_6[0] == True] )        # phase 2 : KEEP

        #deep_5 = deep_4.duplicated(['Symbol']).to_frame()   # pd.duplicated() SERIES result -> DataFrame
        #print ( deep_5[deep_5[0] == True] )                 # select dups - pd.to_frame() default column name = 0

        # scan deep_4 and delete rows with index == deep_6
        print ( "========== DEEP combo no dupes : outlyers described ==========================================" )
        deep_4.drop( deep_6[deep_6[0] == True].index, inplace=True )        # permenantly on the original df
        deep_4 = deep_4.assign(Entropy="" )
        #print ( deep_4 )

        # print ( "========== DEEP combo : Add new column =====================================================" )
        # entropy = {}

        for x in deep_5[deep_5.duplicated(['Symbol'])].Symbol.values:
            row_idx = int(deep_4.loc[deep_4['Symbol'] == x ].index.values)
            cap_size = deep_4.loc[deep_4['Symbol'] == x ].M_B.values
            if cap_size == 'M':
                cap_size = '*Small cap*'
            else:
                cap_size = 'Large cap'
            deep_4.loc[row_idx,'Entropy'] = "Unusual vol "+cap_size

        print ( deep_4 )
        #entropy.update({'*un_vol*': ridx})
        # print ( "Entropy: ", entropy )
        #deep_4.loc[deep_4['Symbol'] == x ]['Entropy'] = "Unusual vol"
        #deep_4['Entropy'] = entropy
        #row = deep_4.loc[deep_4['Symbol'] == x ]
        #print ( "Row: ", row )
        #deep_4['Entropy'] = entropy
        #row = deep_4.insert(rloc, 'Entropy', "Schizzle" )
        #print ( deep_4.loc[deep_4['Symbol'] == x ] )

        # print ( "====================== ALL NaN rows 1 - style 1 =========================" )
        # print ( (deep_4[deep_4['Mkt_cap'].isna()]) )
        # print ( "====================== ALL NaN rows 2 - style 2 =========================" )
        # print ( (deep_4[deep_4['Mkt_cap'].isna()]).iloc[:,[0,5,6]] )    # drop all the known dupes

        # Logic...
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
    return
