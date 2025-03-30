#!/home/orville/venv/devel/bin/python3
from requests_html import HTMLSession
import pandas as pd
import numpy as np
import re
import logging
import argparse
from rich import print

from ml_cvbow import ml_cvbow
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import pipeline

# ML / NLP section #############################################################
class ml_sentiment:
    """
    Class to manage the Global Database of NLP Sentiment data
    and provide statistical analysis of sentiment
    """

    # global accessors
    args = []            # class dict to hold global args being passed in from main() methods
    yfn = None           # Yahoo Finance News reader instance
    mlnlp_uh = None      # URL Hinter instance
    sen_df0 = None
    sen_df1 = None
    sen_df2 = None
    df0_row_count = 0
    ttc = 0             # Total Tokens generated in the scnetcne being analyzed
    twc = 0             # Total Word count in this scentence being analyzed
    yti = 0
    cycle = 0            # class thread loop counter

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s - Instantiate.#{yti}' % cmi_debug )

        self.args = global_args                            # Only set once per INIT. all methods are set globally
        self.yti = yti
        #yfn = yfnews_reader(1, "IBM", global_args )        # instantiate a class of fyn with dummy info
        return

##################################### 1 ####################################
    def save_sentiment(self, yti, data_set):
        """
        Save key ML sentiment info to global sentimennt Dataframe
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.save_sentiment.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )
        x = self.df0_row_count      # get last row added to DF
        x += 1

        # need to add the url hash in here, otherwise I cant do useful analysis
        sym = data_set["sym"]
        art = data_set["article"]
        chk = data_set["chunk"]
        snt = data_set["sent"]
        rnk = data_set["rank"]

        ################################ 6 ####################################
        # now construct our list for concatinating to the dataframe 
        logging.info( f"%s ============= Data prepared for DF =============" % cmi_debug )
        # sen_package = dict(sym=symbol, article=item_idx, chunk=i, sent=sen_result['label'], rank=raw_score )
        self.sen_data = [[ \
                    x, \
                    sym, \
                    art, \
                    chk, \
                    snt, \
                    rnk ]]
        
        self.df0_row = pd.DataFrame(self.sen_data, columns=[ 'Row', 'Symbol', 'Article', 'Chunk', 'Sent', 'Rank' ], index=[x] )
        self.sen_df0 = pd.concat([self.sen_df0, self.df0_row])

        self.df0_row_count = x

        return

##################################### 2 ####################################
    def compute_sentiment(self, symbol, item_idx, scentxt):
        """
        Tokenize and compute scentcen chunk sentiment
        scentxtx = BS4 all <p> zones that look/feel like scentence/paragraph text
        """
        self.yti = item_idx
        cmi_debug = __name__+"::"+self.compute_sentiment.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        logging.info( f'%s - Init ML NLP Tokenizor/Vectorizer...' % cmi_debug )
        vectorz = ml_cvbow(item_idx, self.args)
        stop_words = stopwords.words('english')
        #classifier = pipeline('sentiment-analysis')
        classifier = pipeline(task="sentiment-analysis", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
        tokenizer_mml = classifier.tokenizer.model_max_length
        self.ttc = 0
        self.twc = 0
        print ( f"==== M/L NLP transformer @ max tokens: {tokenizer_mml} : for News article [ {item_idx} ] ====================")
        for i in range(0, len(scentxt)):    # cycle through all scentenses/paragraphs sent to us
            ngram_count = len(re.findall(r'\w+', scentxt[i].text))
            ngram_tkzed = word_tokenize(scentxt[i].text)
            self.ttc += int(len(ngram_tkzed))           # total vectroized tokensgenrated by tokenizer 
            if vectorz.is_scentence(scentxt[i].text):
                chunk_type = "Scent"
            elif vectorz.is_paragraph(scentxt[i].text):
                chunk_type = "Parag"
            else:
                chunk_type = "Randm"
            p_sentiment = classifier(scentxt[i].text, truncation=True)      # WARN: truncating long scentences !!!

            print ( f"Chunk: {i:03} / {chunk_type} / [ n-grams: {ngram_count:03} / tokens: {len(ngram_tkzed):03} / alphas: {len(scentxt[i].text):03} ]", end="" )
            ngram_sw_remv = [word for word in ngram_tkzed if word.lower() not in stop_words]    # remove stopwords
            ngram_final = ' '.join(ngram_sw_remv)   # reform the scentence

            hfw = []    # force hfw list to be empty
            try:
                if int(ngram_count) > 0:
                    vectorz.reset_corpus(ngram_final)
                    vectorz.fitandtransform()
                    #vectorz.view_tdmatrix()     # Debug: dump Vectorized Tranformer info
                    hfw = vectorz.get_hfword()
                else:
                    hfw.append("Empty")
                self.twc += ngram_count    # save and count up Total Word Count
                ngram_sw_remv = ""
                ngram_final= ""
                ngram_count = 0     # words in scnentence/paragraph
                ngram_tkzed = 0     # vectorized tokens genertaed per scentence/paragraph
                sen_result = p_sentiment[0]
                raw_score = sen_result['score']
                rounded_score = np.floor(raw_score * (10 ** 7) ) / (10 ** 7)
                print ( f" / HFN: {hfw} / Sentiment: {sen_result['label']} {(rounded_score * 100):.5f} %")

                # data sentiment data to global sentiment database
                logging.info( f'%s - Save chunklist to DF for article [ {item_idx} ]...' % cmi_debug )
                sen_package = dict(sym=symbol, article=item_idx, chunk=i, sent=sen_result['label'], rank=raw_score )
                self.save_sentiment(item_idx, sen_package)      # page, data
            except RuntimeError:
                print ( f"Model exception !!")
            except ValueError:
                print ( f"Empty vocabulary !!")

        return self.ttc, self.twc, i