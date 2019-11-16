#!/usr/bin/python3

import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate 

with urllib.request.urlopen("https://finance.yahoo.com/gainers/") as url:
    s = url.read()
    soup = BeautifulSoup(s, "html.parser")


# ATTR style search. Results -> Dict
# <tr tag in target merkup line has a very complex 'class=' but the attributes are unique. e.g. 'simpTblRow' is just one unique attribute
all_tag_tr = soup.find_all(attrs={"class": "simpTblRow"})

# This is the target markup line I am scanning for...
# soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )

# Example CSS Selector
#all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )

# create an empty pandas DataFrame with specific column names pre-defined

top_gainers = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )

x = 1    # row counter Also leveraged for unique dataframe key
m = 20
for datarow in all_tag_tr:

    """ 
    if x % m == 0:
        print ( " " )
    else:
        print ( ".", end="" )
    """

    # 1st <td> cell : ticker symbol info & has comment of company name
    # 2nd <td> cell : company name
    # 3rd <td> cell : price
    # 4th <td> cell : $ change
    # 5th <td> cell : % change
    # more cells in <tr> data row...but I'm not interested in them at moment.

    #ticker = datarow.a.get_text()
    #co_name = datarow.a['title']

    # These are the items that I am intersted in...

    # BS4 generator object on "extracted strings"
    extr_strings = datarow.stripped_strings

    co_sym = next(extr_strings)
    co_name = next(extr_strings)
    price = next(extr_strings)
    change = next(extr_strings)
    pct = next(extr_strings)

    # note: Pandas DataFrame : top_gainers pre-initalized as EMPYT on __init__
    ds_data0 = [[ \
               x, \
               co_sym, \
               co_name, \
               price, \
               change, \
               pct ]]

    df_temp0 = pd.DataFrame(ds_data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' ], index=[x] )
    top_gainers = top_gainers.append(df_temp0)    # append this ROW of data into the DataFrame

    x+=1

pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', 30)

print ( top_gainers.sort_values(by='Row', ascending=True ) )    # only do after fixtures datascience dataframe has been built
#print ( tabulate(top_gainers, showindex=False, headers=top_gainers.columns ) )    # only do after fixtures datascience dataframe has been built

