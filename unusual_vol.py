#!/usr/bin/python3

import urllib
import urllib.request
from bs4 import BeautifulSoup


with urllib.request.urlopen("https://old.nasdaq.com/markets/unusual-volume.aspx") as url:
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

#big_table = soup.find_all( "tr" )
#big_table = soup.table
#big_table = soup.find_all( "tbody" )
big_table = soup.find_all( "table" )    # html encapsulated in an iterable array [ ]

#<td class="Va(m) Ta(start) Pstart(6px) Pend(10px) Miw(90px) Start(0) Pend(10px) simpTblRow:h_Bgc($extraLightBlue)  Pos(st) Bgc(white)  Bgc($extraLightBlue)  Ta(start)! Fz(s)" aria-label="Symbol"><label class="Ta(c) Pos(r) Va(tb) Pend(5px) D(n)--print"><input type="checkbox" class="Pos(a) V(h)" value="on"><svg class="Va(m)! H(16px) W(16px) Stk($c-fuji-blue-1-b)! Fill($c-fuji-blue-1-b)! Cur(p)" width="16" height="16" viewBox="0 0 24 24" data-icon="checkbox-checked" style="fill: rgb(0, 0, 0); stroke: rgb(0, 0, 0); stroke-width: 0; vertical-align: bottom;"><path d="M21 3H3v18h18V3zm1 20H2c-.553 0-1-.448-1-1V2c0-.552.447-1 1-1h20c.55 0 1 .448 1 1v20c0 .552-.45 1-1 1zM17.22 7.317L9.74 14.87l-2.96-2.99c-.34-.34-.93-.34-1.27 0-.17.173-.262.403-.262.647 0 .24.094.467.263.637l3.6 3.636c.182.167.41.26.64.26.234 0 .455-.094.623-.265l8.11-8.196c.17-.173.264-.4.264-.64 0-.243-.094-.47-.264-.643-.17-.17-.4-.257-.633-.257-.232 0-.464.086-.634.257z"></path></svg></label><a href="/quote/AMRN?p=AMRN" title="Amarin Corporation plc" class="Fw(600)">AMRN</a><div class="W(3px) Pos(a) Start(100%) T(0) H(100%) Bg($pfColumnFakeShadowGradient) Pe(n) Pend(5px)"></div></td><td class="Va(m) Ta(start) Px(10px) Fz(s)" aria-label="Name"><!-- react-text: 467 -->Amarin Corporation plc<!-- /react-text --></td><td class="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" aria-label="Price (Intraday)"><span class="Trsdu(0.3s) ">20.45</span></td><td class="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" aria-label="Change"><span class="Trsdu(0.3s) Fw(600) C($dataGreen)">+3.54</span></td><td class="Va(m) Ta(end) Pstart(20px) Fw(600) Fz(s)" aria-label="% Change"><span class="Trsdu(0.3s) Fw(600) C($dataGreen)">+20.93%</span></td><td class="Va(m) Ta(end) Pstart(20px) Fz(s)" aria-label="Volume"><span class="Trsdu(0.3s) ">36.106M</span></td><td class="Va(m) Ta(end) Pstart(20px) Fz(s)" aria-label="Avg Vol (3 month)"><!-- react-text: 477 -->6.239M<!-- /react-text --></td><td class="Va(m) Ta(end) Pstart(20px) Pend(10px) W(120px) Fz(s)" aria-label="Market Cap"><span class="Trsdu(0.3s) ">7.361B</span></td><td class="Va(m) Ta(end) Pstart(20px) Fz(s)" aria-label="PE Ratio (TTM)"><span>N/A</span></td><td class="Va(m) Ta(end) Pstart(20px) Pend(6px) Fz(s)" aria-label="52 Week Range"><canvas style="width: 140px; height: 23px;" width="140" height="23"></canvas></td></tr>


#sel_tr_1 = big_table.find_all( "tr", class_="simpTblRow Bgc($extraLightBlue):h BdB Bdbc($finLightGrayAlt) Bdbc($tableBorderBlue):h H(32px) Bgc(white)" )
#sel_tr_1 = BeautifulSoup(big_table, "lxml-xml" )
tag_1 = soup.table      # raw html output
tag_1a = soup.find_all( "div", id="_up" )
tag_1b = soup.find( id="_up" )
tag_1c = tag_1b.table

#tag_1 = big_table.find_all( "tr" )
tag_2 = tag_1c.tbody
tag_3 = tag_1c.tr.get_text()
tag_4 = tag_1c.tr.descendants

x = 0

#print ( "**** TAG_1 ***" )
#print ( tag_1c )
#print ( "===================================================================================" )
#print ( "**** big_table ***" )
#print ( big_table )


print ( "==================== UNUSUAL volume up ====================" )
for datarow in tag_1c.find_all( "tr" )[1:]:    # skips the first <tr> which is table column names

    # 1st <td> cell : ticker symbol info & has comment of company name
    # 2nd <td> cell : company name
    # 3rd <td> cell : price
    # 4th <td> cell : $ change
    # 5th <td> cell : % change
    # more cells follow...but I'm not interested in them at moment.

    extr_strings = datarow.stripped_strings
    co_sym = next(extr_strings)
    co_name = next(extr_strings)
    price = next(extr_strings)
    change = next(extr_strings)
    pct = next(extr_strings)
    vol = next(extr_strings)

    #rowtxt = datarow.get_text()
    #print (rowtxt)

    print ( co_sym, " ", co_name, " ", price, " ", change, " ", pct, " ", vol )

    x+=1
    print ( "============================ ", x, " ===================================" )

print ( " " )
print ( "==================== UNUSUAL volume down ====================" )
tag_1b = soup.find( id="_down" )
tag_1c = tag_1b.table
x = 0
for datarow in tag_1c.find_all( "tr" )[1:]:    # skips the first <tr> which is table column names

    extr_strings = datarow.stripped_strings
    co_sym = next(extr_strings)
    co_name = next(extr_strings)
    price = next(extr_strings)
    change = next(extr_strings)
    pct = next(extr_strings)
    vol = next(extr_strings)

    #rowtxt = datarow.get_text()
    #print (rowtxt)

    print ( co_sym, " ", co_name, " ", price, " ", change, " ", pct, " ", vol )

    x+=1
    print ( "============================ ", x, " ===================================" )


