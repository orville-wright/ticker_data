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
from neo4j import neo4j, GraphDatabase, RoutingControl



# ML / NLP section #############################################################
class db_graph:
    """
    Class to Graph Database operations
    """

    # global accessors
    URI = "neo4j://localhost:7687"
    AUTH = ("neo4j", "Am3li@++")
    args = []            # class dict to hold global args being passed in from main() methods
    driver = None        # driver instance
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

    def con_aopkgdb(self, yti):
        """
        Connect to the Neo4j KnowledgeGraph DB
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.con_aopkgdb.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
        with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
            driver.verify_connectivity()
            logging.info( f'%s - Neo4j KG driver connection.#{yti} established... ' % cmi_debug )
            return driver

##################################### 2 ####################################

    def close_aopkgdb(self, yti, driver):
        """
        Close our connection to the aopkgdb
        """
        driver = GraphDatabase.driver(self.URI, auth=self.AUTH)
        session = driver.session(database="neo4j")
        session.close()
        driver.close()
        return

##################################### 2 ####################################

    def create_sym_node(self, node_data_package):
        """
        Create a Graph NODE
        Assumes driver has been successfully created and saved to self.driver
        """
        with self.driver.session(database="neo4j", default_access_mode=neo4j.WRITE_ACCESS) as session:
            tx = session.begin_transaction()
            # or just use a `with` context instead of try/finally
            node_id = session.execute_write(create_sym_node_tx, name)

    def create_sym_node_tx(tx, name):
        query = ("CREATE (a:Person {name: $name, id: randomUUID()}) "
                "RETURN a.id AS node_id")
        result = tx.run(query, name=name)
        record = result.single()
        return record["node_id"]


