#! python3
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
    mlnlp_uh = None      # URL Hinter instance
    sen_df0 = None       # sentiment for this artile ONLY (gets overwritten each time per article)
    sen_df1 = None
    sen_df2 = None
    df0_row_count = 0
    active_urlhash = None  # Current URL hash being processed
    sen_data = []       # Data to be added to the DataFrame
    art_buffer = []     # Buffer to hold article text for processing
    sentiment_count = { 'positive': 0, 'negative': 0, 'neutral': 0 }  # Sentiment counts for this article
    ttc = 0             # Total Tokens generated in the scnetcne being analyzed
    twc = 0             # Total Word count in this scentence being analyzed
    yti = 0
    cycle = 0            # class thread loop counter

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__
        logging.info( f'%s   - Instantiate.#{yti}' % cmi_debug )

        self.args = global_args                            # Only set once per INIT. all methods are set globally
        self.yti = yti
        return

##################################### 1 ####################################
    def save_sentiment(self, yti, data_set):
        """
        Save key ML sentiment info to global sentimennt Dataframe
        data_set = a dict
        """
        self.yti = yti
        cmi_debug = __name__+"::"+self.save_sentiment.__name__
        logging.info( f"%s - IN.#{yti}" % cmi_debug )
        x = self.df0_row_count      # get last row added to DF
        x += 1

        # need to add the url hash in here, otherwise I cant do useful analysis
        sym = data_set["sym"]
        art = data_set["article"]
        urlhash = data_set["urlhash"]
        chk = data_set["chunk"]
        rnk = data_set["rank"]
        snt = data_set["sent"]

        ################################ 6 ####################################
        # now construct our list for concatinating to the dataframe 
        logging.info( f"%s ============= Data prepared for DF =============" % cmi_debug )
        # sen_package = dict(sym=symbol, article=item_idx, chunk=i, sent=sen_result['label'], rank=raw_score )
        self.sen_data = [[ \
                    x, \
                    sym, \
                    art, \
                    urlhash, \
                    chk, \
                    rnk, \
                    snt ]]
        
        self.df0_row = pd.DataFrame(self.sen_data, columns=[ 'Row', 'Symbol', 'art', 'urlhash', 'chk', 'rnk', 'snt' ], index=[x] )
        self.sen_df0 = pd.concat([self.sen_df0, self.df0_row])

        self.df0_row_count = x

        return

##################################### 2 ####################################
    def compute_sentiment(self, symbol, item_idx, scentxt, urlhash):
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
        self.sentiment_count["positive"] = 0
        self.sentiment_count["negative"] = 0
        self.sentiment_count["neutral"] = 0
        self.active_urlhash = urlhash
        
        if self.args['bool_verbose'] is True:        # Logging level
            print ( f"Transformer max tokens preset: {tokenizer_mml} : for News article [ {item_idx} ]" )

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

            if self.args['bool_verbose'] is True:        # Logging level
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
                
                if self.args['bool_verbose'] is True:        # Logging level
                    print ( f" / HFN: {hfw} / Sentiment: {sen_result['label']} {(rounded_score * 100):.5f} %")

                logging.info( f'%s - Save chunklist to DF for article [ {item_idx} ]...' % cmi_debug )
                sen_package = dict(sym=symbol, urlhash=urlhash, article=item_idx, chunk=i, sent=sen_result['label'], rank=raw_score )
                self.save_sentiment(item_idx, sen_package)      # page, data
                self.sentiment_count[sen_result['label']] += 1  # count sentiment type
            except RuntimeError:
                print ( f"Model exception !!")
            except ValueError:
                print ( f"Empty vocabulary !!")

        return self.ttc, self.twc, i

##################################### 3 ####################################
    def compute_precise_sentiment(self, df_final, positive_c, negative_c, positive_t, negative_t, neutral_t, sentiment_categories):
        """
        Compute precise sentiment analysis based on aggregated data from df_final
        
        Parameters:
        - df_final: DataFrame containing aggregated sentiment data
        - positive_c: Total count of positive sentiment instances
        - negative_c: Total count of negative sentiment instances  
        - positive_t: Mean positive sentiment score
        - negative_t: Mean negative sentiment score
        - neutral_t: Mean neutral sentiment score
        - sentiment_categories: Dictionary mapping sentiment ranges to category descriptions
        
        Returns:
        - Dictionary containing precise sentiment metrics
        """
        cmi_debug = __name__+"::"+self.compute_precise_sentiment.__name__
        logging.info( f'%s - Computing precise sentiment analysis' % cmi_debug )

        # Step 1: Determine overall gross sentiment
        if positive_c > negative_c:
            gross_sentiment = "positive"
            posneg_ratio_pos = positive_c / negative_c if negative_c > 0 else positive_c
            posneg_ratio_neg = 0
            posneg_ratio = posneg_ratio_pos
        elif negative_c > positive_c:
            gross_sentiment = "negative" 
            posneg_ratio_pos = 0
            posneg_ratio_neg = negative_c / positive_c if positive_c > 0 else negative_c
            posneg_ratio = posneg_ratio_neg
        else:
            gross_sentiment = "neutral"
            posneg_ratio_pos = 1.0
            posneg_ratio_neg = 1.0
            
        # Step 2: Make the ratios bigger by factor of 100
        posneg_pos_big = posneg_ratio_pos * 100 if posneg_ratio_pos > 0 else 0
        posneg_neg_big = posneg_ratio_neg * 100 if posneg_ratio_neg > 0 else 0
        
        # Step 3: Compute percentage of information that is positive/negative
        total_sentiment = positive_c + negative_c
        if total_sentiment > 0:
            if gross_sentiment == "positive":
                data_pos_pct = (positive_c / total_sentiment) * 100
                data_neg_pct = (negative_c / total_sentiment) * 100
            else:
                data_pos_pct = (positive_c / total_sentiment) * 100  
                data_neg_pct = (negative_c / total_sentiment) * 100
        else:
            data_pos_pct = 0
            data_neg_pct = 0
            
        # Step 4: Compute precise sentiment scores
        if gross_sentiment == "positive":
            #precise_sent_pos = (posneg_pos_big - (positive_t * 100)) * neutral_t if neutral_t > 0 else posneg_pos_big - (positive_t * 100)
            #precise_sent_neg = (posneg_neg_big - (negative_t * 100)) * neutral_t if neutral_t > 0 else posneg_pos_big - (negative_t * 100)
            precise_sent_pos = (posneg_pos_big - (positive_t * 100)) * neutral_t
            precise_sent_neg = (posneg_neg_big - (negative_t * 100)) * neutral_t
        elif gross_sentiment == "negative":
            precise_sent_pos = ((positive_t * 100) - posneg_neg_big) * neutral_t if neutral_t > 0 else (positive_t * 100) - posneg_neg_big
            precise_sent_neg = ((negative_t * 100) - posneg_neg_big) * neutral_t if neutral_t > 0 else (negative_t * 100) - posneg_neg_big
        else:  # neutral
            precise_sent_pos = 0
            precise_sent_neg = 0
            
        # Round to integers
        precise_sent_pos = round(precise_sent_pos)
        precise_sent_neg = round(precise_sent_neg)
        
        # Step 5: Find matching sentiment categories
        def find_closest_category(score, categories):
            """Find the closest matching category for a given score"""
            if not categories:
                return "Unknown"

            '''
            sentiment_categories = {
                 200: (['Bullish positive', 200]),
                 100: (['Very Positive', 100]),
                 50: (['Positive', 50]),
                 25: (['Trending positive', 25]),
                 0: (['Neutral', 0]),
                 -25: (['Trending negative', -25]),
                 -50: (['Negative', -50]),
                 -100: (['Very Negative', -100]),
                 -200: (['Bearish negative', -200])
                 }
            '''
      
            # Find the key with minimum distance to our score
            closest_key = min(categories.keys(), key=lambda x: abs(x - score))
            return categories[closest_key][0]  # Return the description string

        sentcat_pos = find_closest_category(precise_sent_pos, sentiment_categories)
        sentcat_neg = find_closest_category(precise_sent_neg, sentiment_categories)
        
        # Create results dictionary
        results = {
            'gross_sentiment': gross_sentiment,
            'data_pos_pct': data_pos_pct,
            'data_neg_pct': data_neg_pct,
            'precise_sent_pos': precise_sent_pos,
            'precise_sent_neg': precise_sent_neg,
            'sentcat_pos': sentcat_pos,
            'sentcat_neg': sentcat_neg,
            'posneg_ratio_pos': posneg_ratio_pos,
            'posneg_ratio_neg': posneg_ratio_neg
        }
        
        if round(posneg_ratio,1) <= 1.5:
            gross_sentiment = "NEUTRAL"
        # Step 6: Print the precise sentiment metrics
        print ( f"Overlal: {gross_sentiment.upper()} / Pos-Neg ratio: ({round(posneg_ratio,1)} : 1)" )
        print ( f"Overall: {data_pos_pct:.2f}% {sentcat_pos} - Conf score: {precise_sent_pos}" ) 
        print ( f"Overall: {data_neg_pct:.2f}% {sentcat_neg} - Conf score: {precise_sent_neg}" ) 
        print(f"=============================================================================")
        
        return results
