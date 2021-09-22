#!/usr/bin/python3
import re
import logging
import argparse
import time
import json

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class url_hinter:
    """Class to provide useful hints from url structure """

    # global accessors
    yti = 0                 # Unique instance identifier
    hcycle = 0              # method call  counter
    soup = ""               # BS4 shared handle between UP & DOWN (1 URL, 2 embeded data sets in HTML doc)
    args = []               # class dict to hold global args being passed in from main() methods

    def __init__(self, yti):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info('%s - INIT' % cmi_debug )
        #self.args = global_args    # Only set once per INIT. all methods are set globally
        self.yti = yti
        return

def uhinter(yti, hcycle, url):
    """
    NLP Support function - Exact copy of main::url_hinter()
    Only a few hint types are possible...
    0 = remote stub article - (URL starts with /m/.... and has FQDN:  https://finance.yahoo.com/
    1 = local full article - (URL starts with /news/... and has FQDN: https://finance.yahoo.com/
    2 = local full video - (URL starts with /video/... and has FQDN: https://finance.yahoo.com/
    3 = remote full article - (URL is a pure link to remote article (eg.g https://www.independent.co.uk/news/...)
    9 = Not yet defined
    10 = Error mangled url
    """

    cmi_debug = __name__+"::"+self.uhinter.__name__+".#"+str(self.yti)+str(self.hcycle)
    logging.info('%s - INIT' % cmi_debug )

    uhint_code = { 'm': ('Local/remote stub', 0),
                'news': ('Local article', 1),
                'video': ('Local Video', 2),
                'rfa': ('Remote external', 3),
                'udef': ('Not yet defined', 9),
                'err': ('Error mangled url', 10)
                }
    t_nl = url.path.split('/', 2)       # e.g.  https://finance.yahoo.com/video/disney-release-rest-2021-films-210318469.html
    uhint = uhint_code.get(t_nl[1])     # retrieve uhint code: 0, 1, 2, 3
    logging.info ( f"%s - Hinter logic: {uhint[1]} [{url.netloc}] / {uhint[0]}" % cmi_debug )
    if url.netloc == "finance.yahoo.com":
        logging.info ( f"%s - Inferred hint from URL: {uhint[1]} [{url.netloc}] / {uhint[0]}" % cmi_debug )
        return uhint[1], uhint[0]

    if url.scheme == "https" or url.scheme == "http":    # URL has valid scheme but isn NOT @ YFN
        print ( f"3 / Remote pure url - ", end="" )
        logging.info ( f"%s - Inferred hint from URL: 3 [{url.netloc}] / Remote pure article" % cmi_debug )
        return 3, "Remote external"
    else:
        #print ( f"ERROR_url / ", end="" )
        logging.info ( f"%s - ERROR URL hint is -1 / Mangled URL" % cmi_debug )
        return 10, "Error mangled url"