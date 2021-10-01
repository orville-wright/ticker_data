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
        cmi_debug = __name__+"::"+__name__+".#"+str(self.yti)
        #cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(self.yti)
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
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
        4 = research report - (URL starts with /research/... origin FQDN:  https://finance.yahoo.com/
        9 = Not yet defined
        10 = Error mangled url
        11 = Error state for method
        """

        cmi_debug = __name__+"::uhinter.eng#"+str(self.yti)+"_cyc#"+str(hcycle)
        logging.info('%s - CALLED' % cmi_debug )

        uhint_code = { 'm': ('News snippet', 0),
                    'news': ('News article', 1),
                    'video': ('Video story', 2),
                    'rabs': ('Absolute-ext', 3),
                    'research': ('Research report', 4),
                    'udef': ('Not yet defined', 9),
                    'err': ('Error mangled url', 10),
                    'bad': ('ERROR_unknown_state', 99)
                    }

        logging.info ( f"%s - Hint engine recvd url as: {type(input_url)}" % cmi_debug )
        t_check = isinstance(input_url, str)

        if t_check:
            logging.info ( f"%s - recvd raw url string: {input_url}" % cmi_debug )
            a_url = urlparse(input_url)                 # conv url string into aprsed named tuple object
            if a_url.netloc == "finance.yahoo.com":
                urlp_attr = a_url.path.split('/', 2)                        # work on path=object ONLY
                uhint = uhint_code.get(urlp_attr[1])                            # retrieve uhint code/descr tuple
                logging.info ( f"%s - decoded url as [{a_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                return uhint[1], uhint[0]
            else:
                uhint = uhint_code.get('rabs')            # get our encodings for absolute URL
                logging.info ( f"%s - Extract pure-abs url component: [{a_url.netloc}] u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                if a_url.path == "finance.yahoo.com":                           # paranoid tripple check b/c urls are nortotiously junky
                    logging.info ( f"%s - ERROR mangled url: [{a_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                    error_state = uhint_code.get('err')
                    return error_state[1], error_state[0]
                else:
                    logging.info ( f"%s - decoded url as [{a_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                    return uhint[1], uhint[0]
        else:
            logging.info ( f"%s - recvd pre-parsed urlparse object" % cmi_debug )
            if input_url.netloc == "finance.yahoo.com":                         # e.g.  ParseResult(scheme='https', netloc='finance.yahoo.com', path='/m/49c60293...
                urlp_attr = input_url.path.split('/', 2)                        # work on path=object ONLY
                uhint = uhint_code.get(urlp_attr[1])                            # retrieve uhint code/descr tuple
                logging.info ( f"%s - decoded url as [{input_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                return uhint[1], uhint[0]
            else:
                uhint = uhint_code.get('rabs')            # get our encodings for absolute URL
                logging.info ( f"%s - Extract pure-abs url component: [{input_url.netloc}] u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                if input_url.path == "finance.yahoo.com":                           # paranoid tripple check b/c urls are nortotiously junky
                    logging.info ( f"%s - ERROR mangled url: [{input_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                    error_state = uhint_code.get('err')
                    return error_state[1], error_state[0]
                else:
                    logging.info ( f"%s - decoded url as [{input_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                    return uhint[1], uhint[0]

        error_state = uhint_code.get('bad')             # should NEVER get here - did recv a url raw string or a urlparse object named tuple
        logging.info ( f"%s - ERROR confused logic state: [{a_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
        return error_state[1], error_state[0]           # u: locality code / description


# method #2
    def hstatus(self):
        """
        the engine reports it status
        """
        cmi_debug = __name__+"::"+self.hstatus.__name__+".eng#"+str(self.yti)+"_cyc#"+str(self.hcycle)
        logging.info('%s - CALLED' % cmi_debug )
        logging.info ( f"%s - STATUS / Url hinter engine #{self.yti} / cycle #{self.hcycle}" % cmi_debug )
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
        cmi_debug = __name__+"::"+"confidence_lvl().#1"
        tcode = { 0.0: ('Full article page', 0),
                1.0: ('Stub referr page', 0),
                1.1: ('External-abs link', 1),
                2.0: ('OP-Ed page', 0),
                2.1: ('OP-Ed stub', 1),
                3.0: ('Curated report page', 0),
                3.1: ('Curated report stub', 1),
                4.0: ('Video story page', 0),
                4.1: ('Video story stub', 1),
                5.0: ('Micro-ad insert', 0),
                5.1: ('Micro-ad insert', 1),
                6.0: ('Bulk ad junk', 0),
                6.1: ('Bulk ad junk', 1),
                7.0: ('Research report page', 0),
                7.1: ('Research report stub', 0),
                8.0: ('Unknown thint 8.0', 9),
                9.0: ('Unknown thint 9.0', 9),
                9.9: ('Unknown page structure', 9),
                10.0: ('ERROR unknown state', 9),
                99.9: ('Default NO-YET-SET', 9),
                }
        logging.info ( f"%s - CL decoder input h: {thint}" % cmi_debug )
        thint_descr = tcode.get(thint)    # tuple : page type description / locality code 0=local/1=remote
        return thint_descr
