#!/home/orville/venv/devel/bin/python3
from urllib.parse import urlparse
import logging
import argparse

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class url_hinter:
    """
    Class to provide useful hints from url structure
    """

    # global accessors
    yti = 0                 # Unique instance identifier
    hcycle = 0              # method call counter
    args = []               # class dict to hold global args being passed in from main() methods

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(yti)
        #cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(self.yti)
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )
        self.args = global_args
        self.yti = yti
        return


# method #1
    def uhinter(self, hcycle, recvd_url):
        """
        NLP Support function - Exact copy of main::url_hinter()
        Only a few hint types are possible...
        This is [ u: ] value...
        0 = local full article - (URL starts with /news/... and has FQDN: https://finance.yahoo.com/
        1 = Fake local micro stub article - (URL starts with /m/.... and has FQDN:  https://finance.yahoo.com/
        2 = local full video - (URL starts with /video/... and has FQDN: https://finance.yahoo.com/
        3 = remote full article - (URL is a pure link to remote article:  https://www.independent.co.uk/news/...
        4 = research report - (URL starts with /research/... origin FQDN:  https://finance.yahoo.com/research/reports/.....
        5 = Yahoo Premium plan subscription sign-up page
        9 = Not yet defined
        10 = Error mangled url
        11 = Error state for method
        """

        cmi_debug = __name__+"::uhinter.eng#"+str(self.yti)+"_cyc#"+str(hcycle)
        input_url = recvd_url

        # INFO: U code only - This metainfo does NOT define locality. You cant inferr locality truth from it.
        uhint_code = {
                    'news': ('Local News', 0),
                    'm': ('Fake local micro news', 1),
                    'video': ('Video story', 2),
                    'rabs': ('External publication', 3),
                    'research': ('Research report', 4),
                    'about': ('Premium subscription add', 5),
                    'udef': ('Not yet defined', 9),
                    'err': ('Error mangled url', 10),
                    'bad': ('ERROR_unknown_state', 99)
                    }

        logging.info ( f"%s  - IN Recvd article url: {type(input_url)}" % cmi_debug )
        t_check = isinstance(input_url, str)            # check is url is not a GOOD class:urllib.parse.ParseResult
        # DEBUG : logging.info ( f"%s - Hint url: {input_url}" % cmi_debug )    # {{}} handles urls with %

        if t_check:
            a_url = urlparse(input_url)                 # conv url string into apparsed named tuple object
            if a_url.netloc == "finance.yahoo.com":
                urlp_attr = a_url.path.split('/', 2)    # work on path=object ONLY
                uhint = uhint_code.get(urlp_attr[1])    # retrieve uhint code/descr tuple from split section #1
                logging.info ( f"%s - Logic +0 Decoded url: [{a_url.netloc}] / Type: [{urlp_attr[1]}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                return uhint[1], uhint[0]
            else:
                a_url = urlparse(input_url)
                uhint = uhint_code.get('rabs')            # get our encodings for absolute URL
                logging.info ( f"%s - Logic +1 Extract abs url: [{a_url.netloc}] u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                if a_url.path == "finance.yahoo.com":     # paranoid check b/c urls are nortotiously junky
                    logging.info ( f"%s - Logic +2 / ERROR mangled url: [{a_url.netloc}] / Type: [{a_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                    error_state = uhint_code.get('err')
                    return error_state[1], error_state[0]
                else:
                    logging.info ( f"%s - Logic +3 Decoded url: [{a_url.netloc}] / Type: [{a_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                    return uhint[1], uhint[0]
        else:     # URL recvd as <class 'urllib.parse.ParseResult'>
            logging.info ( f"%s  - Logic +4 Recvd encoded url" % cmi_debug )
            if input_url.netloc == "finance.yahoo.com":        # scheme='https', netloc='finance.yahoo.com', path='/m/49c60293...
                urlp_attr = input_url.path.split('/', 2)                        # work on path=object ONLY
                logging.info ( f"%s  - Logic +4 extracted url hint [1]: [{urlp_attr[1]}]" % cmi_debug )
                uhint = uhint_code.get(urlp_attr[1])                            # retrieve uhint code/descr tuple
                logging.info ( f"%s  - Logic +4 Decoded url: [{input_url.netloc}] / Type: [{urlp_attr[1]}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                return uhint[1], uhint[0]    # u code / description
            else:
                uhint = uhint_code.get('rabs')            # get our encodings for absolute URL
                logging.info ( f"%s - Logic +6 / Decoded url: [{input_url.netloc}] / u:{uhint[1]} / {uhint[0]}" % cmi_debug )
                error_state = uhint_code.get('rabs')
                return error_state[1], error_state[0]

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
        RETURNS a dict of computed confidence level codes & info
        r_uhint = locality confidence code
            : (0=local, 1=remote, 9=ERROR_bad_page_struct, 10=ERROR_unknown_state)  !! may not be correct
        tc = type confidence code (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        ru = Real remote url (extracted)
        su = Fake url from Depth 0 news feed
        Print some nicely formatted info about this discovered article
        NOTE: Locality codes are inferred by decoding the page HTML structure
              They do not match/align with the URL Hint code. Since that could be a 'fake out'
        """
        cmi_debug = __name__+"::"+"confidence_lvl.#1"
        tcode = {
                0.0: ('Full Local article page', 0),
                1.0: ('Fake local micro-stub', 0),
                1.1: ('External publication link', 1),
                2.0: ('OP-Ed page', 0),
                2.1: ('OP-Ed stub', 1),
                3.0: ('Curated report page', 0),
                3.1: ('Curated report stub', 1),
                4.0: ('Video story page', 0),
                4.1: ('Video story stub', 1),
                5.0: ('Micro-ad insert', 1),
                5.1: ('Micro-ad insert', 3),
                6.0: ('Premium subscription add', 0),
                6.1: ('Bulk ad junk', 1),
                7.0: ('Research report page', 0),
                7.1: ('Research report stub', 1),
                8.0: ('Unknown thint 8.0', 9),
                9.0: ('Unknown thint 9.0', 9),
                9.9: ('Unknown page structure', 9),
                10.0: ('ERROR unknown state', 9),
                99.9: ('Default NO-YET-SET', 9),
                }
        logging.info ( f"%s    - Inferr localty hint: [{thint}]" % cmi_debug )
        thint_descr = tcode.get(thint)    # tuple : page type description / locality code 0=local/1=remote
        return thint_descr
