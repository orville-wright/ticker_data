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
allfixtures.ds_df0 = pd.DataFrame(columns=[ 'Time', 'Hid', 'Home', 'Away', 'Aid', 'RankD', 'GDd', \
                                             'GFd', 'GAd', 'Hwin', 'Awin', 'HomeA', 'HGA', 'Weight', 'PlayME'] )

x = 1
for datarow in all_tag_tr1:
    # 1st <td> : ticker symbol info & has comment of company name
    # 2nd <td> : company name
    # 3rd <td> : price
    # 4th <td> : $ change
    # 5th <td> : % change
    # 6th <td> : volume
    # 6th <td> : Avg. vol over 3 months)
    # 7th <td> : Market cap
    # 8th <td> : PE ratio

    #ticker = datarow.a.get_text()
    #co_name = datarow.a['title']
    # BS4 generator object
    extr_strings = datarow.stripped_strings

    co_sym = next(extr_strings)
    co_name = next(extr_strings)
    price = next(extr_strings)
    change = next(extr_strings)
    pct = next(extr_strings)
    vol = next(extr_strings)
    avg_vol = next(extr_strings)
    mktcap = next(extr_strings)

    # print( x, ":", datarow.a['title'], ":", datarow.a.get_text() )

    print ( x, ":", co_sym, co_name, price, change, pct, mktcap )
    print ( "===============================================================" )
    x+=1

"""
    c = 1
    for string in datarow.stripped_strings:
        print ( string, " - ", end="" )
        c+=1
    print ( )
    print ( "ENTRIRE list: ", list(string_test) )
    #print ( "1st NEXT: ", next(string) )
"""

print ( "====================== TAG 1 ========================" )
# print ( all_tag_tr1 )
print ( "====================== TAG 2 ========================" )
#print ( all_tag_tr2 )
