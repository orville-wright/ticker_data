#!/usr/bin/python3

import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse


# logging setup
logging.basicConfig(level=logging.INFO)

def get_topgainers():
    with urllib.request.urlopen("https://finance.yahoo.com/gainers/") as url:
        s = url.read()
        soup = BeautifulSoup(s, "html.parser")

    # ATTR style search. Results -> Dict
    # <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
    all_tag_tr = soup.find_all(attrs={"class": "simpTblRow"})

    # target markup line I am scanning looks like this...
    # soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )

    # Example CSS Selector
    #all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )

    # create empty pandas DataFrame with specific column names pre-defined
    top_gainers = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )

    x = 1    # row counter Also leveraged for unique dataframe key
    for datarow in all_tag_tr:
        # 1st <td> cell : ticker symbol info & has comment of company name
        # 2nd <td> cell : company name
        # 3rd <td> cell : price
        # 4th <td> cell : $ change
        # 5th <td> cell : % change
        # more cells in <tr> data row...but I'm not interested in them at moment.

        # BS4 generator object comes from "extracted strings" BS4 operation (nice)
        extr_strings = datarow.stripped_strings
        co_sym = next(extr_strings)
        co_name = next(extr_strings)
        price = next(extr_strings)
        change = next(extr_strings)
        pct = next(extr_strings)

        co_sym_lj = np.char.ljust(co_sym, 6)       # use numpy to left justify TXT in pandas DF
        co_name_lj = np.char.ljust(co_name, 20)    # use numpy to left justify TXT in pandas DF

        # note: Pandas DataFrame : top_gainers pre-initalized as EMPYT
        # Data treatment:
        # Data is extracted as raw strings, so needs wrangeling...
        #    price - stip out any thousand "," seperators and cast as true decimal via numpy
        #    change - strip out chars '+' and ',' and cast as true decimal via numpy
        #    pct - strip out chars '+ and %' and cast as true decimal via numpy
        ds_data0 = [[ \
                   x, \
                   co_sym_lj, \
                   co_name_lj, \
                   np.float(re.sub('\,', '', price)), \
                   np.float(re.sub('[\+,]', '', change)), \
                   np.float(re.sub('[\+%]', '', pct)) ]]

        df_temp0 = pd.DataFrame(ds_data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' ], index=[x] )
        top_gainers = top_gainers.append(df_temp0)    # append this ROW of data into the DataFrame
        x+=1

    return top_gainers

# Hacking function - keep me arround for a while
def working(self, x, y):
    """simple progress dialogue function"""
    if x % y == 0:
        print ( " " )
    else:
        print ( ".", end="" )
    return

# main() now...
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)

    args = vars(parser.parse_args())
    print ( " " )
    print ( "########## Initalizing ##########" )
    print ( " " )

    # ARGS[] pre-processing - set-ip logging before anything else
    if args['bool_verbose'] is True:
        print ( "Enabeling verbose info logging..." )
        logging.disable(0)     # Log level = NOTSET
    else:
        logging.disable(20)    # Log lvel = INFO

    print ( "Command line args..." )
    print ( parser.parse_args() )
    print ( " " )

    stock_topgainers = get_topgainers()
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth', 30)
    print ( stock_topgainers.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built


if __name__ == '__main__':
    main()
