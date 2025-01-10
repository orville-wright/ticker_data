#! /home/orville/venv/devel/bin/python3
import requests
from requests import Request, Session
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, date
import hashlib
import pandas as pd
import numpy as np
import re
import logging
import argparse
import time
from rich import print

from ml_yahoofinews import yfnews_reader
from ml_urlhinter import url_hinter
from y_topgainers import y_topgainers
from ml_cvbow import ml_cvbow
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import 
from neo4j import GraphDatabase, RoutingControl



# ML / NLP section #############################################################
class db_graph:
    """
    Class to Graph Database operations
    """

    # global accessors
    URI = "neo4j://localhost:7687"
    AUTH = ("neo4j", "Am3li@++")
    args = []            # class dict to hold global args being passed in from main() methods
    yfn = None           # Yahoo Finance News reader instance
    graph_df0 = None
    yti = 0
    cycle = 0            # class thread loop counter

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )

        self.args = global_args                            # Only set once per INIT. all methods are set globally
        self.yti = yti
        return

##################################### 1 ####################################
