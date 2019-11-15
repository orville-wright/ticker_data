#!/usr/bin/python3

import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd


with urllib.request.urlopen("https://finance.yahoo.com/gainers/") as url:
    s = url.read()
    soup = BeautifulSoup(s, "html.parser")

#print (soup.get_text())
#all_tag_a = soup.find_all("td", limit=10)

# Multi-valued attribute
#all_tag_td = soup.find_all( "td", class_="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" )

# extract the entire row
#all_tag_tr1 = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc(white)" )

# RE style
#all_tag_tr1 = soup.find_all(class=re.compile("simpTblRow") )

# ATTR style search sends results -> Dict
all_tag_tr1 = soup.find_all(attrs={"class": "simpTblRow"})


# CSS Selector
#all_tag_tr1 = soup.select( "tr.simpTblRow.Bgc" )

#all_tag_tr2 = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )
#all_tag_tr2 = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($altRowColor" ) 

# create an empty pandas DataFrame with specific column names pre-defined

top_gainers = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )


x = 0

for datarow in all_tag_tr1:

    # 1st <td> cell : ticker symbol info & has comment of company name
    # 2nd <td> cell : company name
    # 3rd <td> cell : price
    # 4th <td> cell : $ change
    # 5th <td> cell : % change
    # more cells follow...but I'm not interested in them at moment.

    #ticker = datarow.a.get_text()
    #co_name = datarow.a['title']

    # These are the items that I am intersted in...

    # BS4 generator object
    extr_strings = datarow.stripped_strings

    co_sym = next(extr_strings)
    co_name = next(extr_strings)
    price = next(extr_strings)
    change = next(extr_strings)
    pct = next(extr_strings)

    # print( x, ":", datarow.a['title'], ":", datarow.a.get_text() )
    # print ( x, ":", co_sym, co_name, price, change, pct )
    # print ( "===============================================================" )
    x+=1

    # note: Pandas DataFrame = top_gainers - allready pre-initalized as EMPYT on __init__
    ds_data0 = [[ \
               x, \
               co_sym, \
               co_name, \
               price, \
               change, \
               pct ]]

    #top_gainers.ds_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change'] )

    df_temp0 = pd.DataFrame(ds_data0, columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change' ], index=[x] )
    top_gainers = top_gainers.append(df_temp0)    # append this ROW of data into the DataFrame

print ( " " )
print ( "======================================== Pandas output ============================================" )
print ( top_gainers.sort_values(by='Row', ascending=True) )    # only do after fixtures datascience dataframe has been built

