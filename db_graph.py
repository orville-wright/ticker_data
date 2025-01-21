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
from transformers import pipeline
from neo4j import GraphDatabase, RoutingControl



# ML / NLP section ################### 0 ##########################################
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
            self.driver = driver
            return driver

##################################### 2 ####################################

    def close_aopkgdb(self, yti, driver):
        """
        Close our connection to the aopkgdb
        """
        driver = GraphDatabase.driver(self.URI, auth=self.AUTH)
        session = self.driver.session(database="neo4j")
        session.close()
        driver.close()
        return

##################################### 3 ####################################

    def create_sym_node(self, ticker_symbol):
        """
        Create a Graph NODE
        Assumes driver has been successfully created and saved to self.driver
        node_data_package = dict of data we want created in GraphDB
        """
        symbol = ticker_symbol.upper()
        cmi_debug = __name__+"::"+self.create_sym_node.__name__+".#"+str(self.yti)
        logging.info( f'%s - Creating graph node for ticker symbol: [ {ticker_symbol} ]...' % cmi_debug )

        with self.driver.session(database="neo4j") as session:
            query = ("CREATE (s:Symbol {symbol: $symbol, id: randomUUID()}) "
                     "RETURN s.id AS node_id")
            result = session.run(query, symbol=symbol)
            record = result.single()
            return record["node_id"]

##################################### 4 ####################################

    def dump_symbols(self, yti):
        """
        Create a Graph NODE
        Assumes driver has been successfully created and saved to self.driver
        node_data_package = dict of data we want created in GraphDB
        """
        cmi_debug = __name__+"::"+self.dump_symbols.__name__+".#"+str(self.yti)
        logging.info( f'%s - RUning Query to dump Sumbols list ]...' % cmi_debug )

        # a Graph node looks like this:
        # its a class of:  neo4j._data.Record
        # <Node element_id='4:174744d5-22cc-4690-90f0-47f1bc98fd53:5' labels=frozenset({'Symbol'}) properties={'symbol': 'nvda', 'id': '6563b467-685e-4520-b4a6-15bfdeeb8812'}>
        # n.data = {'s': {'symbol': 'pfe', 'id': '8df7d4f3-a74a-4a9d-930c-83191bdb88d5'}}

        print ( f"Node symbols in Graph...")
        with self.driver.session(database="neo4j") as session:
            query = ("MATCH ( s:Symbol ) "
                     "RETURN s")
            result = session.run(query)     # Result object
            scount = 1
            buffer = result.fetch(500)      # pull 500 enteries into the buffer
            print ( f"Results BUFFER has [ {len(buffer)} ] elements")

            for i in buffer:                # working on: neo4j._data.Record 
                print ( f"ITEM: {scount} : \t SYMBOL found: {i['s']._properties['symbol']} \t ID: {i['s']._properties['id']}" )
                print ( f"========================================================================================" )
                scount += 1

            rec_done = result.consume()       # ResultSummary objects
            return rec_done

                #print ( f"I: {i}")
                #print ( f"Type I: {type(i)}" )
                #print ( f"Type one_rec: {type(one_record)}" )
                #print ( f"one_rec: {one_record}")
                #print ( f"Symbol found: {one_record[0]['s']['symbol']}")
                #print ( f"Type I[s]: {type(i['s'])}" )              
                #print ( f"{one_record[0].get('symbol')}")
                #print ( f"{one_record[0:3]}")
                #print ( f"{items}")
                #for rec in one_record[0]:
                #print ( f"{rec.keys()}")


##################################### 5 #####################################
    def check_node_exists(self, yti, ticker_symbol):
        """
        Create a Graph NODE
        Assumes driver has been successfully created and saved to self.driver
        node_data_package = dict of data we want created in GraphDB
        """
        yti = yti
        symbol = ticker_symbol.upper()
        cmi_debug = __name__+"::"+self.check_node_exists.__name__+".#"+str(self.yti)
        logging.info( f'%s - Check KG db for existing Symbol [ {symbol} ]' % cmi_debug )

        with self.driver.session(database="neo4j") as session:
            query = ("MATCH (s:Symbol {symbol: $symbol}) "
                     "RETURN s.id IS NOT NULL AS present")

            result = session.run(query, symbol=symbol)     # Result object
            record = result.single()
            return record