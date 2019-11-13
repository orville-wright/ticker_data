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
big_table = soup.find_all( "table", class_="W(100%)" )

#<td class="Va(m) Ta(start) Pstart(6px) Pend(10px) Miw(90px) Start(0) Pend(10px) simpTblRow:h_Bgc($extraLightBlue)  Pos(st) Bgc(white)  Bgc($extraLightBlue)  Ta(start)! Fz(s)" aria-label="Symbol"><label class="Ta(c) Pos(r) Va(tb) Pend(5px) D(n)--print"><input type="checkbox" class="Pos(a) V(h)" value="on"><svg class="Va(m)! H(16px) W(16px) Stk($c-fuji-blue-1-b)! Fill($c-fuji-blue-1-b)! Cur(p)" width="16" height="16" viewBox="0 0 24 24" data-icon="checkbox-checked" style="fill: rgb(0, 0, 0); stroke: rgb(0, 0, 0); stroke-width: 0; vertical-align: bottom;"><path d="M21 3H3v18h18V3zm1 20H2c-.553 0-1-.448-1-1V2c0-.552.447-1 1-1h20c.55 0 1 .448 1 1v20c0 .552-.45 1-1 1zM17.22 7.317L9.74 14.87l-2.96-2.99c-.34-.34-.93-.34-1.27 0-.17.173-.262.403-.262.647 0 .24.094.467.263.637l3.6 3.636c.182.167.41.26.64.26.234 0 .455-.094.623-.265l8.11-8.196c.17-.173.264-.4.264-.64 0-.243-.094-.47-.264-.643-.17-.17-.4-.257-.633-.257-.232 0-.464.086-.634.257z"></path></svg></label><a href="/quote/AMRN?p=AMRN" title="Amarin Corporation plc" class="Fw(600)">AMRN</a><div class="W(3px) Pos(a) Start(100%) T(0) H(100%) Bg($pfColumnFakeShadowGradient) Pe(n) Pend(5px)"></div></td><td class="Va(m) Ta(start) Px(10px) Fz(s)" aria-label="Name"><!-- react-text: 467 -->Amarin Corporation plc<!-- /react-text --></td><td class="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" aria-label="Price (Intraday)"><span class="Trsdu(0.3s) ">20.45</span></td><td class="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" aria-label="Change"><span class="Trsdu(0.3s) Fw(600) C($dataGreen)">+3.54</span></td><td class="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" aria-label="% Change"><span class="Trsdu(0.3s) Fw(600) C($dataGreen)">+20.93%</span></td><td class="Va(m) Ta(end) Pstart(20px) Fz(s)" aria-label="Volume"><span class="Trsdu(0.3s) ">36.106M</span></td><td class="Va(m) Ta(end) Pstart(20px) Fz(s)" aria-label="Avg Vol (3 month)"><!-- react-text: 477 -->6.239M<!-- /react-text --></td><td class="Va(m) Ta(end) Pstart(20px) Pend(10px) W(120px) Fz(s)" aria-label="Market Cap"><span class="Trsdu(0.3s) ">7.361B</span></td><td class="Va(m) Ta(end) Pstart(20px) Fz(s)" aria-label="PE Ratio (TTM)"><span>N/A</span></td><td class="Va(m) Ta(end) Pstart(20px) Pend(6px) Fz(s)" aria-label="52 Week Range"><canvas style="width: 140px; height: 23px;" width="140" height="23"></canvas></td></tr>


#sel_tr_1 = big_table.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc(white)" )
#sel_tr_1 = BeautifulSoup(big_table, "lxml-xml" )
tag_1 = soup.table
tag_2 = soup.tr['class']
tag_3 = soup.tr.get_text()
tag_4 = soup.tr.descendants

x = 1

for datarow in big_table:

    # 1st <td> cell : ticker symbol info & has comment of company name
    # 2nd <td> cell : company name
    # 3rd <td> cell : price
    # 4th <td> cell : $ change
    # 5th <td> cell : % change
    # more cells follow...but I'm not interested in them at moment.

    ticker = datarow.a.get_text()
    co_name = datarow.a['title']

    print ( "A TEXT: ", co_name )

    print ( "DATAROW: ", x, datarow )

    x+=1
    print ( "============================ ", x, " ===================================" )


print ( "TAG_NAME: ", tag_1.name )
print ( "TAG_ATTR_1: ", tag_1.attrs )
print ( "TAG_ATTR_2: ", tag_2 )
print ( "TAG_ATTR_3: ", tag_3 )
print ( "TAG_ATTR_4: ", list(tag_4) )

for string in tag_4.stripped_strings:
    print ( string )
    print ( "========================" )

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
