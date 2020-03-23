#!/usr/bin/python3


from bs4 import BeautifulSoup
import requests
import urllib

def get_live_price(ticker):
    print ( f"IN..." )
    # Send request to marketwatch.com for the given ticker
    print ( f"SEND request for symol {ticker}..." )
    print ( f"URL: {ticker.replace('-', '.')}..." )
    with urllib.request.urlopen("https://bigcharts.marketwatch.com/quickchart/qsymbinfo.asp?symb={ticker}" ) as url:
        print ( f"doing REST get now..." )
        s = url.read()
        soup = BeautifulSoup(s, "html.parser")
        #my_tag = soup.head
        #value = soup.find.h1(attrs={"class": "quote"} )
        #my_tag = soup.find_all(attrs={"class": "fleft price"})
        my_tag = soup.find_all(id="detailedquote")
        url.close()

        #resp = requests.get( f"https://bigcharts.marketwatch.com/quickchart/qsymbinfo.asp?symb={ticker}" )
        # resp = requests.get(f"https://www.marketwatch.com/investing/stock/{ticker.replace('-', '.')}")
        # soup = bs.BeautifulSoup(resp.text, features='lxml')
        # https://bigcharts.marketwatch.com/quickchart/qsymbinfo.asp?symb=TSLA

        #print ( soup )
    # Find HTML element on the page
    #value = soup.find('bg-quote', {'class': 'fleft price'})
        #value = soup.find(attrs={"class": "fleft price"} )
        #self.ul_tag_dataset = self.soup.find(attrs={"class": "My(0) Ov(h) P(0) Wow(bw)"} )
        # Read its value
        print ( f"DATA: {my_tag}" )
        print ( f"RETURN data..." )


get_live_price('CODX')
