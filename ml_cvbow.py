#!/home/orville/venv/devel/bin/python3
from bs4 import BeautifulSoup
import logging
import argparse

# ML capabilities
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords

# logging setup
logging.basicConfig(level=logging.INFO)

#####################################################

class ml_cvbow:
    """
    Machine Learning Helper class for 'Bag of Words' Count Vectorizer that support reading
    finance.yahoo.com docs & text
    """

    # global accessors
    ft_tdmatrix = ""        # term-document matrix learnt from a FIT & TRANSFORM count vectorization
    fo_tokens = ""          # Vocabulary of tokens in a doc (NOT a Term doc Matrix)
    vectorizer = ""         # tokenized & count matrix handle
    corpus = []             # Corpus of text documents we ar working with
    stop_words = []         # Stopwords
    cv_df0 = ""             # DataFrame - Full list of top loserers
    cv_df1 = ""             # DataFrame - Ephemerial list of top 10 loserers. Allways overwritten
    cv_df2 = ""             # DataFrame - Top 10 ever 10 secs for 60 secs
    yti = 0                 # instance UID
    cycle = 0               # class thread loop counter
    args = []

    def __init__(self, yti, global_args):
        cmi_debug = __name__+"::"+self.__init__.__name__+".#"+str(self.yti)
        logging.info('%s - INSTANTIATE' % cmi_debug )
        # init empty DataFrame with present colum names
        self.args = global_args
        stop_words = set(stopwords.words('english'))
        self.vectorizer = CountVectorizer()
        #self.vectorizer = CountVectorizer(stop_words=stopwords)
        return

####################################### 1 #########################################
    def fitandtransform(self):
        """
        Learn the vocabulary dictionary and return document-term matrix.
        This is equivalent to fit followed by transform, but more efficiently implemented
        Build a Term Document Matrix after learning the vocabulary of tokens from the doc.
        WARNING:
        - Method assumes that the CORPUS has been initalized.
        - Allows flexiblty to work on many corpus', many times.
        """
        cmi_debug = __name__+"::"+self.fitandtransform.__name__+".#"+str(self.yti)
        logging.info('%s - IN / Vectorizing corpus ' % cmi_debug )

        # fit_transform is is equivalent to fit followed by transform, but more efficiently implemented
        # the data & attributes available are also differnet to fit followed by transform
        self.ft_tdmatrix = self.vectorizer.fit_transform(self.corpus)
        return self.ft_tdmatrix

####################################### 2 ########################################
    def fitonly(self):
        """
        ONLY learn the vocabulary of tokens in raw docusment, but dont build a Term Document matrix.
        WARNING: Method assumes that the CORPUS has been initalized. This allows flexiblty to work
        on many corpus', many times.
        """
        cmi_debug = __name__+"::"+self.fitonly.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

        # fit_transform is is equivalent to fit followed by transform, but more efficiently implemented
        # the data & attributes available are also differnet to fit followed by transform
        self.fo_tokens = self.vectorizer.fit(self.corpus)
        return self.fo_tokens

####################################### 3 ########################################
    def view_tdmatrix(self):
        """
        Decode the full CSR matrix and view the elements in a human readable table.
        Term_doc_Matrix must already have been FIT and TRASNFORMED.
        """
        cmi_debug = __name__+"::"+self.view_tdmatrix.__name__+".#"+str(self.yti)
        logging.info('%sType - IN' % cmi_debug )

	# working & decoding native scikit-learn CSR data (i.e. Compressed Sparse Row matrix data)
        #print ( f"DATA: {self.ft_tdmatrix.data}" )
        #print ( f"INDICES: {self.ft_tdmatrix.indices}" )
        #print ( f"INDPTR: {self.ft_tdmatrix.indptr}" )
        vmax = self.ft_tdmatrix.max()                         # find highest frequency word (just count, NOT the real word)
        for i in range(0, self.ft_tdmatrix.nnz):              # num of indexed items in this CSR matrix
            for kv in self.vectorizer.vocabulary_.items():    # feature words in vocab dict{}...index=word, value=feature_index_ptr
                if kv[1] == self.ft_tdmatrix.indices[i]:      # {value} = this index?
                    vword = kv[0]                             # yes, get {key} (i.e. the english word)
                    break

            if vmax > 1:
                if vmax == self.ft_tdmatrix.data[i]:			# is this word a highest frequency count word?
                    print ( f"Item: {i} / Indice: {self.ft_tdmatrix.indices[i]} / word: {vword} / Max freq word: {self.ft_tdmatrix.data[i]} times <<" )
                else:
                    print ( f"Item: {i} / Indice: {self.ft_tdmatrix.indices[i]} / word: {vword} / {self.ft_tdmatrix.data[i]}" )
            else:   # all words have equal count = 1, so dont Identify the High Frequency word
                print ( f"Item: {i} / Indice: {self.ft_tdmatrix.indices[i]} / word: {vword} / {self.ft_tdmatrix.data[i]}" )

        return

###################################### 6 ###########################################
# method 13
    def is_scentence(self, p_line):
         if p_line.strip().endswith(('.', '?', '!')):
             return True
         else:
             return False

    def is_paragraph(self, p_line):
         if p_line.count('.') > 1 or p_line.count('?') > 1 or p_line.count('!') > 1:
             return True
         else:
             return False

####################################### 4 ########################################
    def get_hfword(self):
        """
        Decode the full CSR matrix and extract the HIGHEST FREQUENCY WORD from the data.
        Term_doc_Matrix must already have been FIT and TRASNFORMED.
        """
        cmi_debug = __name__+"::"+self.get_hfword.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

	# working & decoding native scikit-learn CSR data (i.e. Compressed Sparse Row matrix data)
        #print ( f"DATA: {self.ft_tdmatrix.data}" )
        #print ( f"INDICES: {self.ft_tdmatrix.indices}" )
        #print ( f"INDPTR: {self.ft_tdmatrix.indptr}" )

        vmax_words = []                 # list to hold English words that == the Highest Frequency count (could be multiple)
        vmax = self.ft_tdmatrix.max()   # find the the highest frequency count word (just count, NOT the real word)
        if vmax > 1:                    # At least 1 word has a frequency occurance greater than 1
                for i in range(0, self.ft_tdmatrix.nnz):                # CYCLE thru matrix of indexed items in this CSR matrix
                    for kv in self.vectorizer.vocabulary_.items():          # SCAN feature words vocab dict{}...index=word, value=feature_index_ptr
                        if kv[1] == self.ft_tdmatrix.indices[i]:            # is {value} = this index?
                            vword = kv[0]               # yes, get {key} (i.e. the english word)
                            vwidx = kv[1]               # and the word index
                            break                       # found the english world in the vocabulary that we are looking at in the matrix

                    if self.ft_tdmatrix.data[i] == vmax:    # is this word a highest frequency count word?
                        vmax_words.append(vword)            # add to list

        elif vmax == 1:
            vmax_words.append("Nominal")
        else:
            vmax_words.append("None")

        vmax_words.append(int(vmax))
        return vmax_words        # the English word with the highest frequency count

####################################### 5 ########################################
    def reset_corpus(self, new_corpus):
        """
        reset the corpus and initialize it with something new
        """
        cmi_debug = __name__+"::"+self.reset_corpus.__name__+".#"+str(self.yti)
        logging.info('%s - IN' % cmi_debug )

	# reset corpus to something new OR empty
        if new_corpus == 0:
            self.corpus = []
            return
        else:
            self.corpus.clear()
            self.vectorizer = CountVectorizer()  # Re-initialize the vectorizer as EMPTY
            self.corpus.append(new_corpus)

        return

