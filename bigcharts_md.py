#! python3
from bs4 import BeautifulSoup
import urllib
import re
import logging

# logging setup
logging.basicConfig(level=logging.INFO)

class bc_quote:
    """
    Get a symbol quote & symbol/company info from bigcharts.marketwatch.com
    Provide 2 methods to access quotes from 2 differnt url pages at bigcharts.marketwatch.com.
    get_basicquote - simple & provides a short format data
    get_quickquote - detailed & provides long format data
    WARN: bigcharts.marketwatch.com market data is ~10-15 mins delayed
    """

    inst_uid = 0
    cycle = 0           # class thread loop counter
    symbol = ""         # Unique company symbol
    prev_symbol = ""    # NOT USED - the ticker previously looked at
    quote = {}          # the final quote data dict

    # DICT qlabels
    # STRING labels to find + test against when populating main data DICT
    #   key = string value of TXT field embedded in source webpage
    #   value = key to be used when building-out core data dict
    # WARN: This dict does not MIRROR the final target QUOTE DICT, due to dupe field complexities
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

# method 1
    def get_basicquote(self, ticker):
        """
        NOTE: This method is slower than method get_quickquote()
        because it accesses a URL endpoint that has rich media elements. So the page builds slower in the extraction.
        But get_basicquote() data elements are structured in a much cleaner & simpler form. i.e. Extraction is a bit simpler.
        It also has 1 data field not available in get_quickquote (i.e. %change)
        This URL endpoint page supports extended URL "?" query_string compponets to control data extraction (but This
        isn't that useful as it controls the embeded rich media elemet output. Which we aren't interested in).
        """

        cmi_debug = __name__+"::"+self.get_basicquote.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        ticker = ticker
        self.symbol = ticker
        url_endpoint = "https://bigcharts.marketwatch.com/quickchart/quickchart.asp?symb="
        url_queryopts = "&insttype=Stock&freq=9&show=True&time=1"

        logging.info('%s - Read request : Basic quote URL endpoint' % cmi_debug )
        with urllib.request.urlopen( f"{url_endpoint}{ticker}{url_queryopts}" ) as url:
            s = url.read()
            logging.info('%s - setup data scrape pointers' % cmi_debug )
            data_soup = BeautifulSoup(s, "html.parser")
            quote_section = data_soup.find(attrs={"id": "quote"} )
            quote_data = quote_section.find_all("tr")
            quote1 = quote_data[2]
            quote2 = quote_data[3]
            logging.info('%s - Close URL' % cmi_debug )
            url.close()

            # Process data Section #1...
            walk_quote1 = quote1.find_all("td")        # Walk 1st data struct <td> is where data is hiding...
            logging.info('%s - Walk section #1 data structure' % cmi_debug )
            for i in walk_quote1:
                if not i.select('img'):                # "Change" field has leading <img> tag
                    logging.info('%s - FOUND Simple data' % cmi_debug )
                    # potentially we have some real TEXT to look at but...doe NULL/None test 1st
                    # b/c the .strip() fails on NULL fields as  you cant .strip() a None structure
                    if type(i.span) is not None:
                        k = i.span.text.strip()        # yes we have text to play with
                        if k in self.qlabels:          # cycle through our known list of labels
                            logging.info('bigcharts_md::get_basicquote.## - INSERT section #1 data into quote dict - %s' % k )
                            self.quote[self.qlabels[k]] = i.div.text.strip()    # add data into quote DICT
                        else:
                            logging.info('%s - ERROR : extract KEY not found in section #1 dataset' % cmi_debug )
                            print ( f"KEY: {k} NOT found in section #1 quote dataset" )
                    else:
                        # this dataset has some NULL / empty data fields
                        logging.info('%s - ERROR : quote section#1 - NULL / Empty data found' % cmi_debug )
                        print ( f"bigcharts_md::get_basicquote.## - Section #1 : Found NULL/Empty data" )
                        # TODO: >> take some actions here <<

                else:   # found the <img> tag, infront of quote data - e.g. 'Change: +0.73'
                    logging.info('%s - in section #1 - Found fancy UP/DOWN image' % cmi_debug )
                    logging.info('%s - in section #1 - READ +/- sign' % cmi_debug )
                    k = i.span.text
                    change_pn = re.sub(r'[\n\ ]', '', i.div.text)    # remove trailing newline
                    logging.info('%s - INSERT +/- sign data into quote dict' % cmi_debug )
                    self.quote['change_s'] = change_pn              # add change_sign into quote DICT

            # Process data Section #2...
            walk_quote2 = quote2.find_all("td")
            logging.info('%s - Walk section #2 data structure' % cmi_debug )
            for i in walk_quote2:
                if not i.select('img'):
                    logging.info('%s - FOUND simple data' % cmi_debug )

                    if type(i.span) is not type(None):                   # capture bad, missing, NULL, Empty data
                        k = i.span.text.strip()
                        if k in self.qlabels:
                            logging.info('bigcharts_md::get_basicquote.## - INSERT section #2 data into quote dict - %s' % k )
                            self.quote[self.qlabels[k]] = i.div.text.strip()    # add to quote DICT
                        else:
                            logging.info('%s - ERROR : extract KEY not found in section #2 dataset' % cmi_debug )
                            print ( f"KEY: {k} NOT found in section #2 quote dataset" )
                    else:
                        logging.info('%s - ERROR : quote section#2 - NULL / Empty data found' % cmi_debug )
                        print ( f"bigcharts_md::get_basicquote.## - Section #2 : Found NULL/Empty data" )
                        # TODO: >> take actions here <<

                else:    # found the <img> tag, infront of quote data - e.g. 'Change: +0.73'
                    logging.info('%s - in section #2 - Found fancy UP/DOWN image' % cmi_debug )
                    logging.info('%s - in section #2 - read change_abs data' % cmi_debug )
                    k = i.span.text.strip()
                    change_abs = re.sub(r'[\n\ ]', '', i.div.text)
                    if k in self.qlabels:
                        self.quote[self.qlabels[k]] = change_abs    # add to quote DICT
                        logging.info('%s - INSERT change_abs data into quote dict' % cmi_debug )
                    else:
                        logging.info('%s - ERROR : KEY not found' % cmi_debug )
                        print ( f"KEY: {k} NOT found in section #2 quote dataset" )

        logging.info('%s - basic_quote() DONE' % cmi_debug )
        return

# method 2
    def get_quickquote(self, ticker):
        """
        NOTE: This method is much faster that get_basicquote()
        The URL endpoint is a minimal webpage doc with almost NO rich meida elements. i.e. page builds very quickly on extraction.
        Although the data elemets require a little extra setup & attention for quick extraction.
        """

        cmi_debug = __name__+"::"+self.get_quickquote.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        ticker = ticker
        self.symbol = ticker
        url_endpoint = "https://bigcharts.marketwatch.com/quickchart/qsymbinfo.asp?symb="
        url_queryopts = "&time=9&freq=1"

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

            qhc = qq_head_co.stripped_strings           # manually work on 1st small generator obj
            ds = next(qhc)
            self.quote['symbol'] = ds.strip()           # add into quote DICT
            qhx = qq_head_data.stripped_strings         # manuall work on 2nd small generator obj
            next(qhx)                                   # manually advance generator
            dc = next(qhx)                              # item #2
            self.quote['change_n'] = dc.strip()         # add into quote DICT

            qlen = len(quote_data)
            for i in range(1, qlen, 2):
                k = quote_data[i].text.strip()
                if k in self.qlabels:
                    logging.info('%s - INSERT data into quote dict' % cmi_debug )
                    self.quote[self.qlabels[k]] = quote_data[i+1].text.strip()    # add to quote DICT
                else:
                    print ( f"KEY: {k} NOT found in quote dataset" )

            flen = len(fin_data)
            for i in range(0, flen, 2):
                clean1 = re.sub(r'[\n\r]', '', fin_data[i].text)
                clean2 = re.sub(r'[\n\r]', '', fin_data[i+1].text)
                clean1 = clean1.strip()
                clean2 = clean2.strip()
                k = clean1
                if k in self.qlabels:
                    logging.info('%s - INSERT data into quote dict' % cmi_debug )
                    self.quote[self.qlabels[k]] = clean2        # add to quote DICT
        return

# method 3
    def q_polish(self):
        """
        Curate & polish data elements in the quote DICT that need wrangeling/cleaning after data extraction.
        Also augment the quote DICT by adding new data elements that we can compute & control.
        Note: method assumes long format get_quickquote() data struct. It only works with get_quickquote().
        *NOT* get_basic_quote() b/c that structure has fewer elements.
        """

        # Its cleaner to do data re-structuring after the quote DICT has been initially populated
        # rather than embed this data wrangeling logic inside the DICT creation method.
        # NOTE: minimal loops. Linear processing = simple & fast.

        cmi_debug = __name__+"::"+self.q_polish.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )

        # change_s = -/+ indicator ('Positive/negative/unchanged') sign
        d = self.quote['change_s']
        d = re.sub(r'[0-9,\.]', '', d)     # remove all nums, "," & "."
        self.quote['change_s'] = d        # update to new value (should be "+" or "-") - TODO: how is UNCHANGED handled?

        # market cap & mkt_cap_scale (i.e. Millions, Billions, Trillions)
        m = self.quote['mkt_cap']
        ms = m[-1]                                 # last char (will be M, B, T)
        if m == 'n/a':                             # no MBT scale (maybe this isn't a regular stock)
            m = 0                                  # set market_cap = $0
            ms = 'X'                               # set scale  = X
            self.quote['mkt_cap'] = 0              # set Mkt_cap = ZERO
            self.quote['mkt_cap_s'] = ms           # M=Million, B=Billion, T=Trillion
        else:
            mv = re.sub(r'[MBT]', '', m)            # remove trailing M, B, T
            self.quote['mkt_cap_s'] = ms           # M=Million, B=Billion, T=Trillion
            self.quote['mkt_cap'] = float(mv)      # set mkt_cap to real num

        # make vol -> a real int
        d = self.quote['vol']
        d = re.sub(r',', '', d)                     # remove "," from num
        self.quote['vol'] = int(d)                 # update orignal STRING vlaue as real INT num

        # Some compound data elements next. Split thgem up & create new DICT fields as needed

        # 52 week range
        r = self.quote['range52w_t']               # e.g. '5.90 to 13.26'
        rt = r.partition(' to ')                   # seperator = ' to ' result is fast, light tupple
        rt_cl = rt[0]
        rt_cl = re.sub(r',', '', rt_cl)
        self.quote['range52w_l'] = float(rt_cl)    # 52 Week HIGH
        rtt_cl = rt[2]
        rtt_cl = re.sub(r',', '', rtt_cl)
        self.quote['range52w_h'] = float(rtt_cl)    # 52 week LOW

        # 52 week HIGH date & value
        h = self.quote['high52w_t']                # e.g. '5.90 to 13.26'
        ht = h.partition(' on ')                   # seperator = ' to ' result is fast, light tupple
        ht_cl = ht[0]
        ht_cl = re.sub(r',', '', ht_cl)
        self.quote['high52w_p'] = float(ht_cl)     # 52 Week HIGH (shuld be same as range52w_h)
        htt_cl = ht[2]
        #htt_cl = re.sub(',', '', htt_cl)
        self.quote['high52w_d'] = htt_cl            # date of 52 week HIGH

        # 52 week LOW date & value
        l = self.quote['low52w_t']                 # e.g. '5.90 to 13.26'
        lt = l.partition(' on ')                   # seperator = ' to ' result is fast, light tupple
        lt_cl = lt[0]
        lt_cl = re.sub(r',', '', lt_cl)
        self.quote['low52w_p'] = float(lt_cl)      # 52 Week LOW (shuld be same as range52w_l)
        self.quote['low52w_d'] = lt[2]             # date of 52 week LOW

        # SHORT interest (num_of_shares) & shorted % (shorted share as % of outstanding shares)
        d = self.quote['short_i_t']                # e.g. '106,614,436 (1.22%)'
        dt = d.partition(' (')                     # seperator = ' ('
        dt0 = re.sub(r',', '', dt[0])               # remove "," from num
        dt2 = re.sub(r'\)', '', dt[2])              # remove trailing ")" from % num
        self.quote['short_i_c'] = dt2              # % of shares shorted

        if dt0[:1].isdigit() is True:              # test if string starts with a num (i.e. 0123456789)
            self.quote['short_i_s'] = int(dt0)     # cast as real INT
        else:
            self.quote['short_i_s'] = 'n/a'        # cast shares shorted as real INT
            self.quote['short_i_c'] = 'n/a'        # set % shorted = n/a if shares shorted is not a num

        # 50day & 200day average price range
        a = self.quote['range_a_p']                # e.g. '10.719 (50-day) 10.2152 (200-day)'
        at = a.split(' ')                          # seperator = ' ' 4 fields split, butonlu 2 of interest
        at_cl = at[0]
        at_cl = re.sub(r',', '', at_cl)
        self.quote['avg50d_p'] = float(at_cl)      # 50 day avg price
        att_cl = at[2]
        att_cl = re.sub(r',', '', att_cl)
        self.quote['avg200d_p'] = float(att_cl)     # 200 day avg price

        # 50day & 200day average volume range
        a = self.quote['range_a_v']                # e.g. '84,447,810 (50-day) 65,450,970 (200-day)'
        at = a.split(' ')                          # seperator = ' ' 4 fields split, butonlu 2 of interest
        at0 = re.sub(r',', '', at[0])               # remove "," from vol nums
        at2 = re.sub(r',', '', at[2])               # remove "," vol nums
        self.quote['avg50d_v'] = int(at0)          # make vol num real int
        self.quote['avg200d_v'] = int(at2)         # make vol num real int

        return
