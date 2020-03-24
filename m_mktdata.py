#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import urllib
import re

# TODO:
    # Make ths a class
    # build a DICT {} for each section
    # make DICT a class gloabl attribute
    # DICT 1 - Basic quote
    # DICT 2 - QUick quote
    # DICT 3 - Basic Finaincials


def get_live_price(ticker):
    with urllib.request.urlopen( f"https://bigcharts.marketwatch.com/quickchart/quickchart.asp?symb={ticker}&insttype=&freq=9&show=True&time=1" ) as url:
        s = url.read()
        data_soup = BeautifulSoup(s, "html.parser")
        quote_section = data_soup.find(attrs={"id": "quote"} )
        #print ( f" ------------------ quote section ---------------------" )
        #print ( quote_section )
        url.close()
        quote_table = quote_section.find("td", attrs={"class": "last"} )
        quote_data = quote_section.find_all("tr")
        quote1 = quote_data[2]
        quote2 = quote_data[3]

        print ( f" ------------------ Basic quote: {ticker} ---------------------" )
        walk_quote1 = quote1.find_all("td")
        for i in walk_quote1:
            if not i.select('img'):
                print ( f"{i.span.text} / {i.div.text}" )
            else:
                change_abs = re.sub('[\n\ ]', '', i.div.text)
                print ( f"{i.span.text} / {change_abs}" )

        walk_quote2 = quote2.find_all("td")
        for i in walk_quote2:
            if not i.select('img'):
                print ( f"{i.span.text} / {i.div.text}" )
            else:
                change_abs = re.sub('[\n\ ]', '', i.div.text)
                print ( f"{i.span.text} / {change_abs}" )

    return


def get_quick_price(ticker):
    with urllib.request.urlopen( f"https://bigcharts.marketwatch.com/quickchart/qsymbinfo.asp?symb={ticker}" ) as url:
        s = url.read()
        data_soup = BeautifulSoup(s, "html.parser")
        qq_head = data_soup.find("h1", attrs={"class": "quote"} )
        qq_head_co = qq_head.find_all('div')[0]
        qq_head_data = qq_head.find_all('div')[3]
        qquote_table = data_soup.find("table", attrs={"id": "quote"} )
        qfin_table = data_soup.find("table", attrs={"class": "financials"} )

        url.close()
        quote_data = qquote_table.find_all("td")
        fin_data = qfin_table.find_all("td")

        print ( f"------------------ Quickquote / simple: {ticker} ---------------------" )
        qhc = qq_head_co.stripped_strings
        print ( f"Symbol: {next(qhc)}" )
        print ( f"Name: {next(qhc)}" )
        qhx = qq_head_data.stripped_strings
        print ( f"Last price: {next(qhx)}" )
        print ( f"Change: {next(qhx)}" )

        print ( f"------------------ Quickquote / price action: {ticker} ---------------------" )
        qlen = len(quote_data)
        for i in range(1, qlen, 2):
            print ( f"{quote_data[i].text} / {quote_data[i+1].text}" )

        print ( f"------------------ Quickquote / Financials: {ticker} ---------------------" )
        flen = len(fin_data)
        for i in range(0, flen, 2):
            clean1 = re.sub('[\n\r]', '', fin_data[i].text)
            clean2 = re.sub('[\n\r]', '', fin_data[i+1].text)
            clean1 = clean1.strip()
            clean2 = clean2.strip()
            print ( f"{clean1} / {clean2}" )

    return

get_live_price('SBUX')
print ( "  " )
get_quick_price('SBUX')
