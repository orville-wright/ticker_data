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

    def create_article_nodes(self, df_final, symbol):
        """
        Create Article Graph NODEs from df_final dataframe using APOC for dynamic labels
        Assumes driver has been successfully created and saved to self.driver
        df_final = dataframe containing article sentiment data
        Creates nodes with static "Article" label and dynamic label based on urlhash
        Checks for existing nodes with Hash_{urlhash} label before creating
        """
        cmi_debug = __name__+"::"+self.create_article_nodes.__name__+".#"+str(self.yti)
        logging.info( f'%s - Creating article nodes from DF...' % cmi_debug )
        symbol = symbol.upper()

        created_nodes = []
        skipped_nodes = []
        
        with self.driver.session(database="neo4j") as session:
            for idx, row in df_final.iterrows():
                # Skip the totals row
                if row['art'] == 'Totals' or pd.isna(row['urlhash']) or row['urlhash'] == '':
                    continue
                
                # Prefix urlhash with 'Hash_' to make it a valid Neo4j label
                dynamic_label = f"Hash_{str(row['urlhash'])}"
                
                # Check if article node with this urlhash already exists
                # Simply check for Article nodes with matching urlhash property
                check_query = "MATCH (n:Article {urlhash: $urlhash}) RETURN n.id AS existing_id LIMIT 1"
                check_result = session.run(check_query, urlhash=str(row['urlhash']))
                existing_record = check_result.single()
                
                if existing_record:
                    # Node already exists, skip creation
                    skipped_nodes.append((existing_record["existing_id"], str(row['urlhash'])))
                    logging.info( f'%s - Article node with label {dynamic_label} already exists, skipping creation for urlhash: {row["urlhash"]}' % cmi_debug )
                    continue
                
                # Node doesn't exist, create it using APOC
                create_query = (
                    "CALL apoc.create.node([$static_label, $dynamic_label], {"
                    "urlhash: $urlhash, "
                    "id: randomUUID(), "
                    "usedby: $usedby, "
                    "art: $art, "
                    "positive: $positive, "
                    "neutral: $neutral, "
                    "negative: $negative, "
                    "psnt: $psnt, "
                    "nsnt: $nsnt, "
                    "zsnt: $zsnt"
                    "}) YIELD node RETURN node.id AS node_id"
                )
                
                result = session.run(create_query,
                    static_label="Article",
                    dynamic_label=dynamic_label,
                    urlhash=str(row['urlhash']),
                    art=int(row['art']),
                    usedby=symbol,
                    positive=float(row['positive']),
                    neutral=float(row['neutral']),
                    negative=float(row['negative']),
                    psnt=float(row['psnt']),
                    nsnt=float(row['nsnt']),
                    zsnt=float(row['zsnt'])
                )
                
                record = result.single()
                created_nodes.append((record["node_id"], str(row['urlhash'])))
                logging.info( f'%s - Created article node with labels [Article, {dynamic_label}]: {record["node_id"]} for urlhash: {row["urlhash"]}' % cmi_debug )
        
        logging.info( f'%s - Summary: {len(created_nodes)} nodes created, {len(skipped_nodes)} nodes skipped (already existed)' % cmi_debug )
        return created_nodes     # Returns a list of tuples (node_id, urlhash) for created nodes

##################################### 7 ####################################

    def create_sym_art_rels(self, ticker_symbol, df_final, agency="Unknown", author="Unknown", published="Unknown", article_teaser="Unknown"):
        """
        Create HAS_ARTICLE relationships between Symbol and Article nodes
        ticker_symbol = the stock symbol
        df_final = dataframe containing article data
        Relationship properties: agency, author, published, article_teaser can be provided
        Checks for existing relationships before creating to avoid duplicates
        """
        symbol = ticker_symbol.upper()
        cmi_debug = __name__+"::"+self.create_sym_art_rels.__name__+".#"+str(self.yti)
        logging.info( f'%s - Creating HAS_ARTICLE relationships for symbol: [ {symbol} ]...' % cmi_debug )

        created_relationships = []
        skipped_relationships = []
        
        with self.driver.session(database="neo4j") as session:
            for idx, row in df_final.iterrows():
                # Skip the totals row
                if row['art'] == 'Totals' or pd.isna(row['urlhash']) or row['urlhash'] == '':
                    continue
                
                # Prefix urlhash with 'Hash_' to match the dynamic label from create_article_nodes
                dynamic_label = f"Hash_{str(row['urlhash'])}"
                
                # Check if relationship already exists
                check_query = (
                    "MATCH (s:Symbol {symbol: $symbol}) "
                    "MATCH (a:Article {urlhash: $urlhash}) "
                    "MATCH (s)-[r:HAS_ARTICLE]->(a) "
                    "RETURN r LIMIT 1"
                )
                
                check_result = session.run(check_query,
                    symbol=symbol,
                    urlhash=str(row['urlhash'])
                )
                existing_rel = check_result.single()
                
                if existing_rel:
                    # Relationship already exists, skip creation
                    skipped_relationships.append(str(row['urlhash']))
                    logging.info( f'%s - REL already exists: {symbol} - {row["urlhash"]}, skipping...' % cmi_debug )
                    continue
                
                # Relationship doesn't exist, create it
                create_query = (
                    "MATCH (s:Symbol {symbol: $symbol}) "
                    f"MATCH (a:{dynamic_label} {{urlhash: $urlhash}}) "
                    "CREATE (s)-[r:HAS_ARTICLE {"
                    "art: $art, "
                    "locality: $locality, "
                    "syndicatedby: $syndicatedby, "
                    "news_agency: $news_agency, "
                    "author: $author, "
                    "published: $published, "
                    "article_teaser: $article_teaser, "
                    "urlhash: $urlhash"
                    "}]->(a) "
                    "RETURN r"
                )
                
                result = session.run(create_query,
                    symbol=symbol,
                    urlhash=str(row['urlhash']),
                    art=int(row['art']),
                    locality="Local",
                    syndicatedby=(ticker_symbol.upper()),
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
                    logging.warning( f'%s - REL Create FAIL urlhash: {row["urlhash"]}' % cmi_debug )
        
        logging.info( f'%s - Summary: {len(created_relationships)} relationships created, {len(skipped_relationships)} relationships skipped (already existed)' % cmi_debug )
        return created_relationships

##################################### 8 ####################################

    def news_agency(self):
        """
        Create YahooFinance NewsAgency node and establish STOCK_NEWS relationships with all Symbol nodes
        Checks for existing YahooFinance node and relationships before creating
        Direction: YahooFinance -[STOCK_NEWS]-> Symbol
        """
        cmi_debug = __name__+"::"+self.news_agency.__name__+".#"+str(self.yti)
        logging.info( f'%s - Creating YahooFinance NewsAgency node and STOCK_NEWS relationships...' % cmi_debug )

        created_relationships = []
        skipped_relationships = []
        yahoo_node_created = False
        
        with self.driver.session(database="neo4j") as session:
            # Check if YahooFinance node already exists
            check_yahoo_query = "MATCH (y:YahooFinance) RETURN y.id AS existing_id LIMIT 1"
            check_result = session.run(check_yahoo_query)
            existing_yahoo = check_result.single()
            
            if existing_yahoo:
                logging.info( f'%s - YahooFinance node exists, skipping...' % cmi_debug )
            else:
                # Create YahooFinance node
                create_yahoo_query = (
                    "CREATE (y:YahooFinance {"
                    "NewsAgency: 'YahooFinance', "
                    "id: randomUUID()"
                    "}) RETURN y.id AS node_id"
                )
                yahoo_result = session.run(create_yahoo_query)
                yahoo_record = yahoo_result.single()
                yahoo_node_created = True
                logging.info( f'%s - Created YahooFinance node: {yahoo_record["node_id"]}' % cmi_debug )
            
            # Get all Symbol nodes
            symbols_query = "MATCH (s:Symbol) RETURN s.symbol AS symbol"
            symbols_result = session.run(symbols_query)
            symbols = [record["symbol"] for record in symbols_result]
            
            logging.info( f'%s - Found {len(symbols)} Symbol nodes to process' % cmi_debug )
            
            # Process each Symbol node
            for symbol in symbols:
                # Check if STOCK_NEWS relationship already exists
                check_rel_query = (
                    "MATCH (y:YahooFinance) "
                    "MATCH (s:Symbol {symbol: $symbol}) "
                    "MATCH (y)-[r:STOCK_NEWS]->(s) "
                    "RETURN r LIMIT 1"
                )
                
                check_rel_result = session.run(check_rel_query, symbol=symbol)
                existing_rel = check_rel_result.single()
                
                if existing_rel:
                    # Relationship already exists, skip creation
                    skipped_relationships.append(symbol)
                    logging.info( f'%s - STOCK_NEWS rel exists for symbol: {symbol}, skipping' % cmi_debug )
                    continue
                
                # Create STOCK_NEWS relationship: YahooFinance -> Symbol
                create_rel_query = (
                    "MATCH (y:YahooFinance) "
                    "MATCH (s:Symbol {symbol: $symbol}) "
                    "CREATE (y)-[r:STOCK_NEWS {"
                    "symbol: $symbol"
                    "}]->(s) "
                    "RETURN r"
                )
                
                rel_result = session.run(create_rel_query, symbol=symbol)
                rel_record = rel_result.single()
                
                if rel_record:
                    created_relationships.append(symbol)
                    logging.info( f'%s - Created STOCK_NEWS rel -> {symbol}' % cmi_debug )
                else:
                    logging.warning( f'%s - Create rel FAILED for symbol: {symbol}' % cmi_debug )
        
        logging.info( f'%s - YF node create: {yahoo_node_created} : {len(created_relationships)} : {len(skipped_relationships)} skipped' % cmi_debug )
        return {
            "node_created": yahoo_node_created,
            "relationships_created": created_relationships,
            "relationships_skipped": skipped_relationships
        }
