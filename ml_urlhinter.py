#!/usr/bin/python3
from urllib.parse import urlparse
import re
import logging
import argparse
import time
import json

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class url_hinter:
    """
    Class to provide useful hints from url structure
    """

    # global accessors
    yti = 0                 # Unique instance identifier
    hcycle = 0              # method call  counter
    args = []               # class dict to hold global args being passed in from main() methods


    # global accessors
    yti = 0                 # Unique instance identifier
    hcycle = 0              # method call  counter
    args = []               # class dict to hold global args being passed in from main() methods

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(self.yti)
        logging.info('%s - INIT<<<<<<<<<<<<<' % cmi_debug )
        self.args = global_args
        self.yti = yti
        return


# method #1
    def uhinter(self, hcycle, input_url):
        """
        NLP Support function - Exact copy of main::url_hinter()
        Only a few hint types are possible...
        0 = remote stub article - (URL starts with /m/.... and has FQDN:  https://finance.yahoo.com/
        1 = local full article - (URL starts with /news/... and has FQDN: https://finance.yahoo.com/
        2 = local full video - (URL starts with /video/... and has FQDN: https://finance.yahoo.com/
        3 = remote full article - (URL is a pure link to remote article (eg.g https://www.independent.co.uk/news/...)
        9 = Not yet defined
        10 = Error mangled url
        11 = Error state for method
        """

        cmi_debug = __name__+"::uhinter.eng#"+str(self.yti)+"_cyc#"+str(hcycle)
        logging.info('%s - CALLED' % cmi_debug )

        uhint_code = { 'm': ('Local-remote stub', 0),
                    'news': ('Local article', 1),
                    'video': ('Local video', 2),
                    'rabs': ('Remote-absolute', 3),
                    'udef': ('Not yet defined', 9),
                    'err': ('Error mangled url', 10),
                    'bad': ('ERROR_unknown_state', 99)
                    }

        urlp_attr = input_url.path.split('/', 2)       # e.g.  ParseResult(scheme='https', netloc='finance.yahoo.com', path='/m/49c60293...
        uhint = uhint_code.get(urlp_attr[1])           # retrieve uhint code as tuple

        if input_url.netloc == "finance.yahoo.com":
            logging.info ( f"%s - Hint engine decoded: {uhint[1]} [{input_url.netloc}] / {uhint[0]}" % cmi_debug )
            return uhint[1], uhint[0]
        else:
            a_url = urlparse(input_url)               # treat input_url like its a raw absolute FQDN URL
            uhint = uhint_code.get('rabs')            # get our encodings for absolute URL
            logging.info ( f"%s - Recieved pure-absolute url: {uhint[1]} [{a_url.netloc}] / {uhint[0]}" % cmi_debug )
            if a_url.path != "finance.yahoo.com":
                return uhint[1], uhint[0]
            elif a_url.path == "finance.yahoo.com":
                uhint = uhint_code.get('bad')            # get our encodings for absolute URL
                logging.info ( f"%s - ERROR confused logic state / {uhint[1]} [{a_url.netloc}] / {uhint[0]}" % cmi_debug )
                return uhint[1], uhint[0]
            else:
                uhint = uhint_code.get('err')            # get our encodings for absolute URL
                logging.info ( f"%s - Recieved Mangled URL / {uhint[1]} [{a_url.netloc}] / {uhint[0]}" % cmi_debug )
                return uhint[1], uhint[0]

        error_state = uhint_code.get('bad')             # should NEVER get here
        return uhint[1], uhint[0]


# method #2
    def hstatus(self):
        """
        the engine reports it status
        """
        cmi_debug = __name__+"::"+self.hstatus.__name__+".eng#"+str(self.yti)+"_cyc#"+str(self.hcycle)
        logging.info('%s - CALLED' % cmi_debug )
        logging.info ( f"%s - Url hinter engine #{self.yti} / cycle #{self.hcycle}" % cmi_debug )
        return self.yti, self.hcycle



# method #3
    def confidence_lvl(self, thint):
        """
        NLP Support function #1
        INFO: Does *not* print any output
        RETURNSL a dict of computed confidence level codes & info
        r_uhint = locality confidence code (0=remote, 1=local, 9=ERROR_bad_page_struct, 10=ERROR_unknown_state)
        tc = type confidence code (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        ru = Real remote url (extracted)
        su = Fake url from Depth 0 news feed
        Print some nicely formatted info about this discovered article
        NOTE: Locality codes are inferred by decoding the page HTML structure
              They do not match/align with the URL Hint code. Since that could be a 'fake out'
        """
        cmi_debug = __name__+"::"+"confidence_ind().#1"
        tcode = { 0.0: 'Real news - local page',
                1.0: 'Real news - remote-stub',
                1.1: 'Real news - remote-abs',
                2.0: 'OP-Ed - local',
                2.1: 'OP-Ed - remote',
                3.0: 'Curated report - local',
                3.1: 'Curated report - remote',
                4.0: 'Video story - local',
                4.1: 'Video story - remote',
                5.0: 'Micro-ad - local',
                5.1: 'Micro-ad - remote',
                6.0: 'Bulk ad - local',
                6.0: 'Bulk ad - remote',
                7.0: 'Unknown thint 7.0',
                8.0: 'Unknown thint 8.0',
                9.0: 'Unknown thing 9.0',
                9.9: 'Unknown page structure',
                10.0: 'ERROR unknonw state',
                99.9: 'DEfault NO-YET-SET'
                }
        logging.info ( f"%s    - hint code recieved: {thint}" % cmi_debug )
        thint_descr = tcode.get(thint)
        return thint_descr
