#!/usr/bin/python3

import urllib
import urllib.request
from bs4 import BeautifulSoup


with urllib.request.urlopen("https://finance.yahoo.com/gainers/") as url:
    s = url.read()

soup = BeautifulSoup(s, "html.parser")

#print (soup.get_text())
#all_tag_a = soup.find_all("td", limit=10)

# Multi-valued attribute
#all_tag_td = soup.find_all( "td", class_="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" )

# extract the entire row
#all_tag_tr = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc(white)" )
#all_tag_tr = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue)" )
#all_tag_tr = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($extraLightBlue) " )

odd_data_row = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc(white) " )
evn_data_row = soup.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc($altRowColor) " )


# big_table = soup.find_all( "table", class_="W(100%)" )


#sel_tr_1 = big_table.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc(white)" )
#sel_tr_1 = BeautifulSoup(big_table, "lxml-xml" )


# tag_1 = soup.table
# tag_2 = soup.tr['class']
# tag_3 = soup.tr.get_text()
# tag_4 = soup.tr.descendants

x = 1

# for datarow in big_table:
for data in odd_data_row:

    # 1st <td> cell : ticker symbol info & has comment of company name
    # 2nd <td> cell : company name
    # 3rd <td> cell : price
    # 4th <td> cell : $ change
    # 5th <td> cell : % change
    # more cells follow...but I'm not interested in them at moment.

    ticker = data.a.get_text()
    co_name = data.a['title']

    print ( "DATA : ", x, "  ", ticker )
    print ( "DATA 2: ", x, "  ", co_name )
    print ( "ALL DATA: ", x, " ", data )

    x+=1
    print ( "============================ ", x, " ===================================" )


print ( "MAIN STRING", odd_data_row )

# These are the items that I am intersted in...
"""
    # BS4 generator object
    for string in datarow.stripped_strings:
        #extr_strings = datarow.stripped_strings
        print ( string, " - ", end="" )
        c+=1
    print ( )
    #print ( "ENTIRE list: list(

    #co_sym = next(extr_strings)
    #co_name = next(extr_strings)
    #price = next(extr_strings)
    #change = next(extr_strings)
    #pct = next(extr_strings)

    #print( x, ":", datarow.a['title'], ":", datarow.a.get_text() )

    #print ( x, ":", co_sym, co_name, price, change, pct )
    #print ( "===============================================================" )
    #x+=1
"""

"""
    c = 1
    for string in datarow.stripped_strings:
        print ( string, " - ", end="" )
        c+=1
    print ( )
    print ( "ENTRIRE list: ", list(string_test) )
    #print ( "1st NEXT: ", next(string) )
"""


print ( "======================" )

#print ( all_tag_td )
