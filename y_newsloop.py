#!/usr/bin/python3
import urllib
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
from datetime import datetime
import threading
import hashlib


# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class y_newsfilter:
    """Class to extract a specific stock's News from finance.yahoo.com"""

    # global accessors
    n_df0 = ""          # DataFrame - Full list of top gainers
    n_df1 = ""          # DataFrame - Ephemerial list of top 10 gainers. Allways overwritten
    n_df2 = ""          # DataFrame - Top 10 ever 10 secs for 60 secs
    soup = ""           # the entire HTML doc
    ul_tag_dataset = ""      # BS4 handle of the <tr> extracted data
    inst_uid = 0
    cycle = 0           # class thread loop counter
    symbol = ""         # Unique company symbol

    def __init__(self, i, symbol, global_args):
        # WARNING: There is/can-be NO checking to ensure this is a valid/real symbol
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT inst' % cmi_debug )
        self.args = global_args
        # init empty DataFrame with present colum names
        self.n_df0 = pd.DataFrame(columns=[ 'Row', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.n_df1 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.n_df2 = pd.DataFrame(columns=[ 'ERank', 'Symbol', 'Co_name', 'Cur_price', 'Prc_change', 'Pct_change', 'Mkt_cap', 'M_B', 'Time'] )
        self.inst_uid = i
        self.symbol = symbol
        return

# method #1
    def get_news_list(self):
        """Connect to finance.yahoo.com and extract (scrape) the raw data out of"""
        """the complex webpage [Stock:News ] html data table. Returns a BS4 handle."""

        cmi_debug = __name__+"::"+self.get_news_list.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        news_url = "https://finance.yahoo.com/quote/" + self.symbol + "/news?p=" + self.symbol      # form the correct URL
        logging.info('%s - URL:' % (cmi_debug) )
        print ( f"Extract news for: SDC @: {news_url}" )
        with urllib.request.urlopen(news_url) as url:
            s = url.read()
            logging.info('%s - read html stream' % cmi_debug )
            self.soup = BeautifulSoup(s, "html.parser")
        logging.info('%s - save data object handle' % cmi_debug )
        #self.ul_tag_dataset = self.soup.find_all(attrs={"class": "C(#959595)"} )        # the section in the HTML page we focus-in on
        self.ul_tag_dataset = self.soup.find(attrs={"class": "My(0) Ov(h) P(0) Wow(bw)"} )
        # <div class="C(#959595) Fz(11px) D(ib) Mb(6px)">
        logging.info('%s - close url handle' % cmi_debug )
        url.close()
        return

    def follow_news_link(self, url):
        """Follow a URL of a news article and extract the data for deeper processing of an individual news article"""
        """Note: calling this recurisvely will be network expensive...but that is the plan"""

        cmi_debug = __name__+"::"+self.follow_news_link.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        deep_url = url      # pass in the url that we want to deeply analyze
        logging.info('%s - Follow URL:' % (cmi_debug) )
        logging.info('%s - read html stream' % cmi_debug )
        with urllib.request.urlopen(deep_url) as url:
            f = url.read()
            logging.info('%s - read html stream' % cmi_debug )
            soup = BeautifulSoup(f, "html.parser")

        logging.info('%s - ' % cmi_debug )
        #
        # fnl_tag_dataset = soup.find_all('a')
        fnl_tag_dataset = soup.div.find_all(attrs={'class': 'D(tbc)'} )
        logging.info('%s - close url handle' % cmi_debug )
        url.close()
        return fnl_tag_dataset

# method #2
    def build_news(self):
        """Build-out a fully populated Pandas DataFrame containg all the"""
        """extracted/scraped fields from the html/markup table data"""
        """Wrangle, clean/convert/format the data correctly."""

        cmi_debug = __name__+"::"+self.build_news.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        time_now = time.strftime("%H:%M:%S", time.localtime() )
        logging.info('%s - Drop all rows from DF0' % cmi_debug )
        self.n_df0.drop(self.n_df0.index, inplace=True)
        x = 1    # row counter Also leveraged for unique dataframe key

        li_superclass = self.ul_tag_dataset.find_all(attrs={"class": "js-stream-content Pos(r)"} )
        li_subset = self.ul_tag_dataset.find_all('li')
        mini_headline = self.ul_tag_dataset.div.find_all(attrs={'class': 'C(#959595)'})
        #micro_headline = self.soup.find_all("i") #attrs={'class': 'Mx(4px)'})

        for datarow in range(len(li_subset)):
            html_element = li_subset[datarow]
            print ( f"====== News item: #{x} ===============" )
            print ( f"News outlet: {html_element.div.find(attrs={'class': 'C(#959595)'}).string }" )
            #print ( f"News outlet2: {datarow[0].contents}" )
            """print ( f"DOT: {html_element.i.find(attrs={'class': 'Mx(4px)'}) }" )"""
            print ( f"News item URL: {html_element.a.get('href')}" )
            print ( f"News headline: {html_element.a.text}" )
            print ( "Brief: {:.400}".format(html_element.p.text) )    # truncate long New Brief headlines to max 400 chars

            # generate a unuque hash for each new URL so that we can easily test for dupes
            url_prehash = html_element.a.get('href')
            result = hashlib.sha256(url_prehash.encode())
            print ( f"Hash encoded URL: {result.hexdigest()}" )
            x += 1

            # This is somewhat complicated DATA EXTRACTION, beciase we are now getting into the
            # dirty details & low-levl data components within specific HTML data pages
            fnl_deep_link = 'https://finance.yahoo.com' + url_prehash
            a_subset = self.follow_news_link(fnl_deep_link)
            print ( f"Tag sections in news page: {len(a_subset)-1}" )
            for erow in range(len(a_subset)):       # cycyle through how-ever many sections there are in this dataset
                #print ( f"======= Follow news link deep link element: {erow} / {len(a_subset)-1} ========" )
                #print ( f"== {erow}: == URL.div element: {a_subset[erow].name}" )
                if a_subset[erow].time:     # if this element rown has a <time> tag...
                    nztime = a_subset[erow].time['datetime']
                    ndate = a_subset[erow].time.text
                    dt_ISO8601 = datetime.strptime(nztime, "%Y-%m-%dT%H:%M:%S.%fz")
                    # TODO: calculate age of this news article
                    # TODO: parse out date component, subtract date from today, calculate num_of_days old
                    #pzconv_date = datetime.strptime(nztime, "%Y-%m-%d")
                    #pzconv_time = datetime.strptime(nztime, "%H:%M:S")
                    # print ( f"News: {erow} / Time: {a_subset[erow].time['datetime']}", end="" )  # Zulu time string
                    # print ( f" / Date: {a_subset[erow].time.text}" )         # Pretty data
                    if a_subset[erow].div:  # if this element row has a sub <div>
                        nauthor = a_subset[erow].div.find(attrs={'itemprop': 'name'}).text
                        #print ( f"News: {erow} / Authour: {a_subset[erow].div.find(attrs={'itemprop': 'name'}).text }" )      # Authour
                    # print ( f"== {erow}: == URL.div element: {a_subset[erow]}" )

                # DEBUG
                if self.args['bool_xray'] is True:        # DEBUG Xray
                    for tag in a_subset[erow].find_all(True):
                        print ( f"{tag.name}, ", end="" )
                        #if tag a_subset[erow].time exists inside this element...
                        print ( " " )

                logging.info('%s - Cycle: Follow New Link deep extratcion' % cmi_debug )
            print ( f"Details: {ndate} / Time: {dt_ISO8601} / Author: {nauthor}" )

        logging.info('%s - Extracted NEWS' % cmi_debug )
        return x        # number of rows extracted

# method #3
# Hacking function - keep me arround for a while
    def prog_bar(self, x, y):
        """simple progress dialogue function"""
        if x % y == 0:
            print ( " " )
        else:
            print ( ".", end="" )
        return

# method #4
    def topg_listall(self):
        """Print the full DataFrame table list of Yahoo Finance Top Gainers"""
        """Sorted by % Change"""

        cmi_debug = __name__+"::"+self.topg_listall.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.n_df0.sort_values(by='Pct_change', ascending=False ) )    # only do after fixtures datascience dataframe has been built
        return

# method #5
    def build_top10(self):
        """Get top 15 gainers from main DF (df0) -> temp DF (df1)"""
        """df1 is ephemerial. Is allways overwritten on each run"""

        cmi_debug = __name__+"::"+self.build_top10.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )

        logging.info('%s - Drop all rows from DF1' % cmi_debug )
        self.n_df1.drop(self.n_df1.index, inplace=True)
        logging.info('%s - Copy DF0 -> ephemerial DF1' % cmi_debug )
        self.n_df1 = self.n_df0.sort_values(by='Pct_change', ascending=False ).head(15).copy(deep=True)    # create new DF via copy of top 10 entries
        self.n_df1.rename(columns = {'Row':'ERank'}, inplace = True)    # Rank is more accurate for this Ephemerial DF
        self.n_df1.reset_index(inplace=True, drop=True)    # reset index each time so its guaranteed sequential
        return

# method #7
    def print_top10(self):
        """Prints the Top 10 Dataframe"""

        cmi_debug = __name__+"::"+self.print_top10.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        pd.set_option('display.max_rows', None)
        pd.set_option('max_colwidth', 30)
        print ( self.n_df1.sort_values(by='Pct_change', ascending=False ).head(15) )
        return

# method #6
    def build_tenten60(self, cycle):
        """Build-up 10x10x060 historical DataFrame (df2) from source df1"""
        """Generally called on some kind of cycle"""

        cmi_debug = __name__+"::"+self.build_tenten60.__name__+".#"+str(self.inst_uid)
        logging.info('%s - IN' % cmi_debug )
        self.n_df2 = self.n_df2.append(self.n_df1, ignore_index=False)    # merge top 10 into
        self.n_df2.reset_index(inplace=True, drop=True)    # ensure index is allways unique + sequential
        return
