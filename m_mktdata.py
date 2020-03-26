#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import urllib
import re
import logging

# logging setup
logging.basicConfig(level=logging.INFO)

# TODO:
    # Basic quote: split 52 week range into 2 data elemets
    # Finaincials: split short interest into 2 data elements
    #              split 52-week high into 2 elemets
    #              split 52-week low into 2 elements
    #              split average price into 2 elemets (50-day & 200-day)
    #              split average volume into 2 elements (50-day & 200-day)
    #
    # Make ths a class
    # build a DICT {} for each section
    # make DICT a class gloabl attribute
    # DICT 1 - Basic quote
    # DICT 2 - QUick quote
    # DICT 3 - Basic Finaincials
    # Before adding data to DICT's...
    #       make sure all numeric strings are converted to float before addig to DICT's
    #       remove () from strings
    #       remove () from negative numbers and formats as negative float
    #       re-compute data strings as true date objects
class mw_quote:
    """Get a live quote via a fast data extraction from a fast web URL endpoint.
    There are 2 differnt URL endpoints leveraged via  www.marketwatch.com. Both are simple
    URL pages have almost zero rich media elements embedded in them. i.e. they are almost 100% TXT.
    This means they build very quickly in the extraction process."""

    # class global accessors
    inst_uid = 0
    cycle = 0           # class thread loop counter
    symbol = ""         # Unique company symbol
    prev_symbol = ""    # the ticker we previously looked at
    quote = {}          # the core data dict

    # DICT qlabels = STRING data labels to find & test against when populating main data DICT
    #   key = string value of TXT field embedded in source webpage
    #   value = key to be used when building-out core data dict
    # WARN: This dict does not EXACTLY match the taregt core data DICT, due to dupe field complexities !!
    qlabels = {'52 Week Range:': 'range52w', '52-Week EPS:': 'eps52w', '52-Week High:': 'high52w', \
                '52-Week Low:': 'low52w', 'Ask:': 'ask', 'Average Price:': 'avg50d_p', \
                'Average Volume:': 'avg50d_v', 'Bid:': 'bid', 'Change:': 'change_s', \
                'Company Name:': 'co_name', 'Dow Jones Industry:': 'dowjones', 'Ex Div. Amount:': 'ex_diva', \
                'Ex Div. Date:': 'ex_divd', 'Exchange:': 'exch', 'High:': 'high', 'Last:': 'last', \
                'Low:': 'low', 'Market Cap:': 'mkt_cap', 'Open:': 'open', 'P/E Ratio:': 'pe_ratio', \
                'Percent Change:': 'change_p', 'Shares Outstanding:': 'shares_o', 'Symbol': 'symbol', \
                'Short Interest:': 'short_i', 'Volume:': 'vol', 'Yield:': 'yield' }

    def __init__(self, i, global_args):
        """ WARNING: symbol is set to NONE at instantiation."""
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT inst' % cmi_debug )
        self.args = global_args
        self.inst_uid = i
        self.symbol = 'NONE'
        self.prev_symbol = 'NONE'
        return

    #### methods
    def get_basicquote(self, ticker):
        # NOTE: This method is slower than method #2 (quickquote)
        #       because it uses a URL endpoint that has some rich media elements. So the page builds slower in the extraction.
        #       Although, it's data elements are structured in a much cleaner & simpler form. i.e. Extraction is a bit simpler.
        #       It also has 1 data field not available in method #2 (i.e. %change)
        #       The URL endpoint can also take an extended URL "?" quoery_string compponet to control data extraction (but This
        #        isn't that useful as it controls the embeded rich media elemet output. Which we aren't interested in).

        cmi_debug = __name__+"::"+self.get_basicquote.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        ticker = ticker
        self.symbol = ticker
        url_endpoint = "https://bigcharts.marketwatch.com/quickchart/quickchart.asp?symb="
        url_queryopts = "&insttype=&freq=9&show=True&time=1"

        with urllib.request.urlopen( f"{url_endpoint}{ticker}{url_queryopts}" ) as url:
            s = url.read()
            data_soup = BeautifulSoup(s, "html.parser")
            quote_section = data_soup.find(attrs={"id": "quote"} )
            quote_table = quote_section.find("td", attrs={"class": "last"} )
            quote_data = quote_section.find_all("tr")
            quote1 = quote_data[2]
            quote2 = quote_data[3]
            url.close()

            print ( f" ------------------ Basic quote: {ticker} ---------------------" )
            # walk the 1st embeded data structure...
            walk_quote1 = quote1.find_all("td")
            for i in walk_quote1:
                if not i.select('img'):         # special treatment for "Change" field. Has <img> tag
                    k = i.span.text.strip()
                    print ( f"{i.span.text.strip()}  {i.div.text.strip()}" )
                    if k in self.qlabels:
                        self.quote[self.qlabels[k]] = i.div.text.strip()    # build core DICT
                    else:
                        print ( f"KEY: {k} NOT found !" )
                else:       # treat 'Change: +0.73' as special item.
                    k = i.span.text
                    change_pn = re.sub('[\n\ ]', '', i.div.text)    # clean up
                    print ( f"{i.span.text}  {change_pn}" )
                    self.quote['change_s'] = change_pn    # build core DICT

            # walk the 2nd embeded data structure...
            walk_quote2 = quote2.find_all("td")
            for i in walk_quote2:
                if not i.select('img'):
                    k = i.span.text.strip()
                    print ( f"{i.span.text.strip()}  {i.div.text.strip()}" )
                    if k in self.qlabels:
                        self.quote[self.qlabels[k]] = i.div.text.strip()    # build core DICT
                    else:
                        print ( f"NO key found !" )
                else:
                    k = i.span.text.strip()
                    change_abs = re.sub('[\n\ ]', '', i.div.text)
                    print ( f"{i.span.text}  {change_abs}" )
                    if k in self.qlabels:
                        self.quote[self.qlabels[k]] = change_abs    # build core DICT
                    else:
                        print ( f"NO key found !" )

        return


    def get_quickquote(self, ticker):
        # NOTE: This method is much faster
        #       The URL is a minimal webpage doc with almost NO rich meida elements. i.e. page builds very quickly on extraction
        #       Although the data elemets require a little extra setup & attention for quick extraction

        cmi_debug = __name__+"::"+self.get_quickquote.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        ticker = ticker
        self.symbol = ticker
        url_endpoint = "https://bigcharts.marketwatch.com/quickchart/qsymbinfo.asp?symb="

        with urllib.request.urlopen( f"{url_endpoint}{ticker}" ) as url:
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
            ds = next(qhc)
            print ( f"Symbol: {ds}" )
            self.quote['symbol:'] = ds.strip()          # build core DICT
            print ( f"Name: {next(qhc)}" )              # ignored from adding into quote DICT
            qhx = qq_head_data.stripped_strings
            print ( f"Last price: {next(qhx)}" )        # ignored from adding into quote DICT
            dc = next(qhx)
            print ( f"Change: {dc}" )                   # manually manage this DUPEd data item (appears 3 times in source data)
            self.quote['change_n'] = dc.strip()         # build core DICT

            print ( f"------------------ Quickquote price action: {ticker} ---------------------" )
            qlen = len(quote_data)
            for i in range(1, qlen, 2):
                k = quote_data[i].text.strip()
                print ( f"{quote_data[i].text} {quote_data[i+1].text}" )
                if k in self.qlabels:
                    self.quote[self.qlabels[k]] = quote_data[i+1].text.strip()    # build core DICT
                else:
                    print ( f"NO key found !" )

            print ( f"------------------ Quickquote / Financials: {ticker} ---------------------" )
            flen = len(fin_data)
            for i in range(0, flen, 2):
                clean1 = re.sub('[\n\r]', '', fin_data[i].text)
                clean2 = re.sub('[\n\r]', '', fin_data[i+1].text)
                clean1 = clean1.strip()
                clean2 = clean2.strip()
                print ( f"{clean1} {clean2}" )
                k = clean1
                if k in self.qlabels:
                    self.quote[self.qlabels[k]] = clean2
        return
