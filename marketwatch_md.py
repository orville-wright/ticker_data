#!/home/orville/venv/devel/bin/python3
from bs4 import BeautifulSoup
import urllib
import re
import logging

# logging setup
logging.basicConfig(level=logging.INFO)

class mw_quote:
    """Get a live quote from a fast web URL endpoint.
    There are 2 slightly differnt but yet similar URL's leveraged via  www.marketwatch.com.
    Both are simple pages & have near-zero rich media elements in them. (i.e. almost 100% TXT)
    This means they build quickly during the extraction process.
    The core URL is: https://bigcharts.marketwatch.com/quickchart/qsymbinfo.asp
    WARN: This URL provides market data that is ~10-15 mins delayed
    """

    # class global accessors
    inst_uid = 0
    cycle = 0           # class thread loop counter
    symbol = ""         # Unique company symbol
    prev_symbol = ""    # NOT USED - the ticker previously looked at
    quote = {}          # the final quote data dict

    # DICT qlabels
    # STRING labels to find + test against when populating main data DICT
    #   key = string value of TXT field embedded in source webpage
    #   value = key to be used when building-out core data dict
    # WARN: This dict does not MIRROR the fina taregt QUOTE DICT, due to dupe field complexities
    qlabels = {'52 Week Range:': 'range52w_t', '52-Week EPS:': 'eps52w', '52-Week High:': 'high52w_t', \
                '52-Week Low:': 'low52w_t', 'Ask:': 'ask', 'Average Price:': 'range_a_p', \
                'Average Volume:': 'range_a_v', 'Bid:': 'bid', 'Change:': 'change_s', \
                'Company Name:': 'co_name', 'Dow Jones Industry:': 'dowjones', 'Ex Div. Amount:': 'ex_diva', \
                'Ex Div. Date:': 'ex_divd', 'Exchange:': 'exch', 'High:': 'high', 'Last:': 'last', \
                'Low:': 'low', 'Market Cap:': 'mkt_cap', 'Open:': 'open', 'P/E Ratio:': 'pe_ratio', \
                'Percent Change:': 'change_c', 'Shares Outstanding:': 'shares_o', 'Symbol:': 'symbol', \
                'Short Interest:': 'short_i_t', 'Volume:': 'vol', 'Yield:': 'yield' }

    def __init__(self, i, global_args):
        """ WARNING: symbol is set to NONE at instantiation."""
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{i}' % cmi_debug )
        self.args = global_args
        self.inst_uid = i
        self.symbol = 'NONE'
        self.prev_symbol = 'NONE'
        return

    #### methods
    def get_quote(self, ticker):
        # NOTE: This method is has average data extraction performance
        #       It leverages a modern rich Javascript URL endpoint that has many rich media elements.
        #       The page builds much slower in the extraction & is far more compex to navigate & extract data from.
        #       The key data elements are far more deeply embeded in very complex HTML structures.
        #       Comapred to the old simple TXT based URL at https://bigcharts.marketwatch.com

        cmi_debug = __name__+"::"+self.get_quote.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        ticker = ticker
        self.symbol = ticker
        url_endpoint = ( f"https://www.marketwatch.com/investing/stock/{ticker}" )
        url_queryopts = "?mod=home-page"

        # **** robot page hack ***
        u_values = {'_gid': 'GA1.2.1635298290.1585325464', \
                  'kuid': 'utizzienf', \
                  'usr_prof_v2': 'eyJpYyI6M30%3D', \
                  '_ncg_id_': '16fd531b9d4-d5059ed1-6668-4a16-b696-c114236bba83', \
                  'ab_uuid': '4f58185c-50c8-4d43-8eb7-3d4fda9fe62c', \
                  'usr_bkt': '63L1D4y2F9', \
                  '_ncg_g_id_': '167f04e4-2d20-4d46-b377-cae17ef19f4d', \
                  'kayla': 'g=070adfde82e0468dac1e2eeecbad776d' }

        udata = urllib.parse.urlencode(u_values)
        udata = udata.encode('ascii')
        user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36"

        headers = {'User-Agent': user_agent}
        # mw_req = urllib.request.Request(url_endpoint, udata, headers)
        req = urllib.request.Request(url_endpoint, udata, headers)
        with urllib.request.urlopen(req) as url:
            s = url.read()
            print ( f" ------------------ Basic header: {ticker} ---------------------" )
            print ( f"URL: {url_endpoint}" )
            print ( f" ------------------ URL.read() ---------------------" )
            print ( f"FULL URL: {req.get_full_url()}" )
            print ( f"STATUS: {url.status} / REASON: {url.reason}" )
            print ( f"RESPONSE: {req.header_items()}" )
            print ( f"REQ HEADER ITEMS: {req.header_items()}" )
            print ( f"READ DATA: {s}" )

            #resp = requests.get( f"{url_endpoint}" )

            #with urllib.request.urlopen( req ) as url:
            #with urllib.request.urlopen( f"{url_endpoint}{ticker}{url_queryopts}" ) as url:
            #s = url.text
            #data_soup = BeautifulSoup(resp.text, "html.parser")
            print ( f" ------------------ BS4.html.parse ---------------------" )
            data_soup = BeautifulSoup(s, "html.parser")
            print ( data_soup )

        """
        q_head = data_soup.find("div", attrs={"class": "element element--company"} )
        q_intraday = data_soup.find("div", attrs={"class": "element element--intraday"} )
        q_sector1 = data_soup.find("div", attrs={"class": "intraday__sector"} )
        q_prevclose = data_soup.find("div", attrs={"class": "intraday__close"} )
        q_srangeb = data_soup.find("div", attrs={"class": "column column--full supportive-data"} )
        q_keydata = data_soup.find("div", attrs={"class": "column column--full left clearfix"} )
        q_perf = data_soup.find("div", attrs={"class": "column column--full right clearfix"} )


        quote_section = data_soup.find(attrs={"id": "quote"} )
        quote_table = quote_section.find("td", attrs={"class": "last"} )
        quote_data = quote_section.find_all("tr")
        quote1 = quote_data[2]
        quote2 = quote_data[3]

        #url.close()

        print ( f" ------------------ Basic header: {ticker} ---------------------" )
        head_symb = q_head.find("span", attrs={"class": "company__ticker"} )
        print ( f"Symbol: {head_symb.text}" )
        print ( f"Exchange: {head_symb.next_element.text}" )
        print ( f"Company name: {head_symb.h1.next_element.text}" )

        walk_quote1 = quote1.find_all("td")
        for i in walk_quote1:
            if not i.select('img'):         # special treatment for "Change" field. Has <img> tag
                k = i.span.text.strip()
                # print ( f"{i.span.text.strip()}  {i.div.text.strip()}" )      # DEBUG
                if k in self.qlabels:
                    self.quote[self.qlabels[k]] = i.div.text.strip()    # add to quote DICT
                else:
                    print ( f"KEY: {k} NOT found !" )
            else:       # treat 'Change: +0.73' as special item.
                k = i.span.text
                change_pn = re.sub('[\n\ ]', '', i.div.text)    # clean up
                # print ( f"{i.span.text}  {change_pn}" )                       # DEBUG
                self.quote['change_s'] = change_pn    # add to quote DICT

        # walk the 2nd embeded data structure...
        walk_quote2 = quote2.find_all("td")
        for i in walk_quote2:
            if not i.select('img'):
                k = i.span.text.strip()
                # print ( f"{i.span.text.strip()}  {i.div.text.strip()}" )      # DEBUG
                if k in self.qlabels:
                    self.quote[self.qlabels[k]] = i.div.text.strip()    # add to quote DICT
                else:
                    print ( f"NO key found !" )
            else:
                k = i.span.text.strip()
                change_abs = re.sub('[\n\ ]', '', i.div.text)
                # print ( f"{i.span.text}  {change_abs}" )                      # DEBUG
                if k in self.qlabels:
                    self.quote[self.qlabels[k]] = change_abs    # add to quote DICT
                else:
                    print ( f"NO key found !" )
        """

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

            # print ( f"------------------ Quickquote / simple: {ticker} ---------------------" )
            # manuall traverse a small set of data elements - looping through small generators is pointless
            qhc = qq_head_co.stripped_strings           # manually work on 1st small generator obj
            ds = next(qhc)
            self.quote['symbol'] = ds.strip()           # add into quote DICT

            qhx = qq_head_data.stripped_strings         # manuall work on 2nd small generator obj
            # print ( f"Last price: {next(qhx)}" )      # item #1 IGNORED - DUPE data ite,. Not needed again
            next(qhx)                                   # manually advance generator
            dc = next(qhx)                              # item #2
            self.quote['change_n'] = dc.strip()         # add into quote DICT

            # print ( f"------------------ Quickquote price action: {ticker} ---------------------" )
            qlen = len(quote_data)
            for i in range(1, qlen, 2):
                k = quote_data[i].text.strip()
                # print ( f"{quote_data[i].text} {quote_data[i+1].text}" )          # DEBUG
                if k in self.qlabels:
                    self.quote[self.qlabels[k]] = quote_data[i+1].text.strip()    # add to quote DICT
                else:
                    print ( f"NO key found !" )

            # print ( f"------------------ Quickquote / Financials: {ticker} ---------------------" )
            flen = len(fin_data)
            for i in range(0, flen, 2):
                clean1 = re.sub('[\n\r]', '', fin_data[i].text)
                clean2 = re.sub('[\n\r]', '', fin_data[i+1].text)
                clean1 = clean1.strip()
                clean2 = clean2.strip()
                # print ( f"{clean1} {clean2}" )                                    # DEBUG
                k = clean1
                if k in self.qlabels:
                    self.quote[self.qlabels[k]] = clean2        # add to quote DICT
        return

    def q_polish(self):
        """This method curates & polishes a few data elements in the quote DICT
        that need additinoal treatement after the inital build-out. It also
        augments the quote DICT with new data elements.
        """

        # Its cleaner to do data re-structuring after the quote DICT has been initially populated
        # rather than embed this data wrangeling logic inside the DICT creation method.
        # NOTE: No loops. Linear, simple & fast.

        cmi_debug = __name__+"::"+self.q_polish.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )

        # wragle change_s (i.e. Positive/negative/unchanged )
        d = self.quote['change_s']
        d = re.sub('[0-9,\.]', '', d)     # remove all nums, "," & "."
        self.quote['change_s'] = d       # update to new value (shuld be "+" or "-") - TODO: how is UNCHANGED handled?

        # market cap & mkt_cap scale (i.e. Millions, Billions, Trillions)
        m = self.quote['mkt_cap']
        ms = m[-1]                                  # access last char (will be M, B, T)
        mv = re.sub('[MBT]', '', m)                 # remove trailing M, B, T
        self.quote['mkt_cap_s'] = ms                # M=Million, B=Billion, T=Trillion
        self.quote['mkt_cap'] = float(mv)           # mkt_cap as real num

        # make vol -> a real int
        d = self.quote['vol']
        d = re.sub(',', '', d)                      # remove "," from num
        self.quote['vol'] = int(d)                  # update orignal STRING vlaue as real INT num

        # split compound data elements & create new DICT fields as needed

        # 52 week range
        r = self.quote['range52w_t']                 # e.g. '5.90 to 13.26'
        rt = r.partition(' to ')                     # seperator = ' to ' result is fast, light tupple
        self.quote['range52w_l'] = float(rt[0])      # 52 Week HIGH
        self.quote['range52w_h'] = float(rt[2])      # 52 week LOW

        # 52 week HIGH date & value
        h = self.quote['high52w_t']                 # e.g. '5.90 to 13.26'
        ht = h.partition(' on ')                    # seperator = ' to ' result is fast, light tupple
        self.quote['high52w_p'] = float(ht[0])      # 52 Week HIGH (shuld be same as range52w_h)
        self.quote['high52w_d'] = ht[2]             # date of 52 week HIGH

        # 52 week LOW date & value
        l = self.quote['low52w_t']                 # e.g. '5.90 to 13.26'
        lt = l.partition(' on ')                   # seperator = ' to ' result is fast, light tupple
        self.quote['low52w_p'] = float(lt[0])      # 52 Week LOW (shuld be same as range52w_l)
        self.quote['low52w_d'] = lt[2]             # date of 52 week LOW

        # SHORT interest (num_of_shares) & shorted % (shorted share as % of outstanding shares)
        d = self.quote['short_i_t']                # e.g. '106,614,436 (1.22%)'
        dt = d.partition(' (')                     # seperator = ' ('
        dt0 = re.sub(',', '', dt[0])               # remove "," from num
        dt2 = re.sub('\)', '', dt[2])              # remove trailing ")" from % num
        self.quote['short_i_s'] = int(dt0)         # make shares shorted an real INT
        self.quote['short_i_c'] = dt2              # % of shares shorted

        # 50day & 200day average price range
        a = self.quote['range_a_p']                # e.g. '10.719 (50-day) 10.2152 (200-day)'
        at = a.split(' ')                          # seperator = ' ' 4 fields split, butonlu 2 of interest
        self.quote['avg50d_p'] = float(at[0])      # 50 day avg price
        self.quote['avg200d_p'] = float(at[2])     # 200 day avg price

        # 50day & 200day average volume range
        a = self.quote['range_a_v']                # e.g. '84,447,810 (50-day) 65,450,970 (200-day)'
        at = a.split(' ')                          # seperator = ' ' 4 fields split, butonlu 2 of interest
        at0 = re.sub(',', '', at[0])               # remove "," from vol nums
        at2 = re.sub(',', '', at[2])               # remove "," vol nums
        self.quote['avg50d_v'] = int(at0)          # make vol num real int
        self.quote['avg200d_v'] = int(at2)         # make vol num real int

        return
