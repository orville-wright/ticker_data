#! python3
from requests_html import HTMLSession
import logging
import argparse
import dotenv
import os
import pandas as pd
from rich import print

from neo4j import GraphDatabase, RoutingControl



# ML / NLP section ################### 0 ##########################################
class db_graph:
    """
    Class to Graph Database operations
    """

    # global accessors
    URI = None
    AUTH = None
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

        # Load environment variables from .env file
        load_status = dotenv.load_dotenv()
        if load_status is False:
            raise RuntimeError('Environment variables not loaded.')
        else:
            # Retrieve Neo4j Aura credentials from environment variables
            self.URI = os.getenv("NEO4J_URI")
            USERNAME = os.getenv("NEO4J_USERNAME")
            PASSWORD = os.getenv("NEO4J_PASSWORD")
            self.AUTH = (USERNAME, PASSWORD)


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

    def create_sym_node(self, ticker_symbol, sentiment_df=None):
        """
        Create a Symbol Graph NODE with enhanced sentiment data
        Assumes driver has been successfully created and saved to self.driver
        sentiment_df = sent_ai.sen_df3 dataframe with sentiment analysis data
        """
        symbol = ticker_symbol.upper()
        cmi_debug = __name__+"::"+self.create_sym_node.__name__+".#"+str(self.yti)
        logging.info( f'%s - Creating enhanced graph node for ticker symbol: [ {ticker_symbol} ]...' % cmi_debug )

        with self.driver.session(database="neo4j") as session:
            if sentiment_df is not None and not sentiment_df.empty:
                # Extract sentiment data from first row
                row = sentiment_df.iloc[0]
                query = (
                    "CREATE (s:Symbol {"
                    "symbol: $symbol, "
                    "id: randomUUID(), "
                    "sentiment: $sentiment, "
                    "ratio: $ratio, "
                    "p_pct: $p_pct, "
                    "p_cat: $p_cat, "
                    "p_score: $p_score, "
                    "n_pct: $n_pct, "
                    "n_cat: $n_cat, "
                    "n_score: $n_score, "
                    "p_mean: $p_mean, "
                    "n_mean: $n_mean, "
                    "z_mean: $z_mean"
                    "}) RETURN s.id AS node_id"
                )
                result = session.run(query, 
                    symbol=symbol,
                    sentiment=row['Sentiment'],
                    ratio=float(row['Ratio']),
                    p_pct=float(row['P_pct']),
                    p_cat=row['P_cat'],
                    p_score=int(row['P_score']),
                    n_pct=float(row['N_pct']),
                    n_cat=row['N_cat'],
                    n_score=int(row['N_score']),
                    p_mean=float(row['P_mean']),
                    n_mean=float(row['N_mean']),
                    z_mean=float(row['Z_mean'])
                )
            else:
                # Fallback to basic symbol node if no sentiment data
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
            print ( f"Results BUFFER has [ {len(buffer)} ] elements\n")

            for i in buffer:                # working on: neo4j._data.Record 
                print ( f"ITEM: {scount} : \t SYMBOL found: {i['s']._properties['symbol']} \t ID: {i['s']._properties['id']}" )
                print ( f"========================================================================================" )
                scount += 1

            rec_done = result.consume()       # ResultSummary objects
            return rec_done

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

##################################### 6 ####################################

    def create_article_nodes(self, df_final):
        """
        Create Article Graph NODEs from df_final dataframe
        Assumes driver has been successfully created and saved to self.driver
        df_final = dataframe containing article sentiment data
        """
        cmi_debug = __name__+"::"+self.create_article_nodes.__name__+".#"+str(self.yti)
        logging.info( f'%s - Creating article nodes from df_final dataframe...' % cmi_debug )

        created_nodes = []
        
        with self.driver.session(database="neo4j") as session:
            for idx, row in df_final.iterrows():
                # Skip the totals row
                if row['art'] == 'Totals' or pd.isna(row['urlhash']) or row['urlhash'] == '':
                    continue
                    
                query = (
                    "CREATE (a:Article {"
                    "urlhash: $urlhash, "
                    "id: randomUUID(), "
                    "art: $art, "
                    "positive: $positive, "
                    "neutral: $neutral, "
                    "negative: $negative, "
                    "psnt: $psnt, "
                    "nsnt: $nsnt, "
                    "zsnt: $zsnt"
                    "}) RETURN a.id AS node_id"
                )
                
                result = session.run(query,
                    urlhash=str(row['urlhash']),
                    art=int(row['art']),
                    positive=float(row['positive']),
                    neutral=float(row['neutral']),
                    negative=float(row['negative']),
                    psnt=float(row['psnt']),
                    nsnt=float(row['nsnt']),
                    zsnt=float(row['zsnt'])
                )
                
                record = result.single()
                created_nodes.append((record["node_id"], str(row['urlhash'])))
                logging.info( f'%s - Created article node: {record["node_id"]} for urlhash: {row["urlhash"]}' % cmi_debug )
        
        return created_nodes

##################################### 7 ####################################

    def create_symbol_article_relationships(self, ticker_symbol, df_final, agency="Unknown", author="Unknown", published="Unknown", article_teaser="Unknown"):
        """
        Create HAS_ARTICLE relationships between Symbol and Article nodes
        ticker_symbol = the stock symbol
        df_final = dataframe containing article data
        Relationship properties: agency, author, published, article_teaser can be provided
        """
        symbol = ticker_symbol.upper()
        cmi_debug = __name__+"::"+self.create_symbol_article_relationships.__name__+".#"+str(self.yti)
        logging.info( f'%s - Creating HAS_ARTICLE relationships for symbol: [ {symbol} ]...' % cmi_debug )

        created_relationships = []
        
        with self.driver.session(database="neo4j") as session:
            for idx, row in df_final.iterrows():
                # Skip the totals row
                if row['art'] == 'Totals' or pd.isna(row['urlhash']) or row['urlhash'] == '':
                    continue
                
                query = (
                    "MATCH (s:Symbol {symbol: $symbol}) "
                    "MATCH (a:Article {urlhash: $urlhash}) "
                    "CREATE (s)-[r:HAS_ARTICLE {"
                    "locality: $locality, "
                    "news_agency: $news_agency, "
                    "author: $author, "
                    "published: $published, "
                    "article_teaser: $article_teaser, "
                    "urlhash: $urlhash"
                    "}]->(a) "
                    "RETURN r"
                )
                
                result = session.run(query,
                    symbol=symbol,
                    urlhash=str(row['urlhash']),
                    locality="Local",
                    news_agency=agency,
                    author=author,
                    published=published,
                    article_teaser=article_teaser
                )
                
                record = result.single()
                if record:
                    created_relationships.append(str(row['urlhash']))
                    logging.info( f'%s - Created HAS_ARTICLE relationship for urlhash: {row["urlhash"]}' % cmi_debug )
                else:
                    logging.warning( f'%s - Failed to create relationship for urlhash: {row["urlhash"]}' % cmi_debug )
        
        return created_relationships
