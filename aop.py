#! python3
import urllib.request
import pandas as pd
import logging
import argparse
import time
import threading
from urllib.parse import urlparse
from rich import print

# logging setup
logging.basicConfig(level=logging.INFO)

# my private classes & methods
from y_topgainers import y_topgainers
from y_daylosers import y_daylosers
from y_smallcaps import smallcap_screen
from nasdaq_uvoljs import un_volumes
from nasdaq_quotes import nquote
from shallow_logic import combo_logic
from bigcharts_md import bc_quote
from ml_urlhinter import url_hinter
from ml_nlpreader import ml_nlpreader
from y_techevents import y_techevents
from nasdaq_wrangler import nq_wrangler
from y_cookiemonster import y_cookiemonster
from ml_sentiment import ml_sentiment
from db_graph import db_graph

# Globals
work_inst = 0
global args
args = {}
global parser
parser = argparse.ArgumentParser(description="Entropy apperture engine")
parser.add_argument('-a','--allnews', help='ML/NLP News sentiment AI for all stocks', action='store_true', dest='bool_news', required=False, default=False)
parser.add_argument('-c','--cycle', help='Ephemerial top 10 every 10 secs for 60 secs', action='store_true', dest='bool_tenten60', required=False, default=False)
parser.add_argument('-d','--deep', help='Deep converged multi data list', action='store_true', dest='bool_deep', required=False, default=False)
parser.add_argument('-n','--newsai', help='ML/NLP News sentiment AI for 1 stock', action='store', dest='newsymbol', required=False, default=False)
parser.add_argument('-p','--perf', help='Tech event performance sentiment', action='store_true', dest='bool_te', required=False, default=False)
parser.add_argument('-q','--quote', help='Get ticker price action quote', action='store', dest='qsymbol', required=False, default=False)
parser.add_argument('-s','--screen', help='Small cap screener logic', action='store_true', dest='bool_scr', required=False, default=False)
parser.add_argument('-t','--tops', help='show top ganers/losers', action='store_true', dest='bool_tops', required=False, default=False)
parser.add_argument('-u','--unusual', help='unusual up & down volume', action='store_true', dest='bool_uvol', required=False, default=False)
parser.add_argument('-v','--verbose', help='verbose error logging', action='store_true', dest='bool_verbose', required=False, default=False)
parser.add_argument('-x','--xray', help='dump detailed debug data structures', action='store_true', dest='bool_xray', required=False, default=False)

# Threading globals
extract_done = threading.Event()
yti = 1
uh = url_hinter(1, args)        # anyone needs to be able to get hints on a URL from anywhere

#######################################################################
# Global method for __main__
# thread function #1
# DEPRECATED

def do_nice_wait(topg_inst):
    """Threaded wait that does work to build out the 10x10x60 DataFrame"""
    logging.info('y_topgainers:: IN Thread - do_nice_wait()' )
    logging.info('y_topgainers::do_nice_wait() -> inst: %s' % topg_inst.yti )
    for r in range(6):
        logging.info('do_nice_wait() cycle: %s' % topg_inst.cycle )
        time.sleep(5)    # wait immediatley to let remote update
        topg_inst.get_topg_data()       # extract data from finance.Yahoo.com
        topg_inst.build_tg_df0()
        topg_inst.build_top10()
        topg_inst.build_tenten60(r)     # pass along current cycle
        print ( ".", end="", flush=True )
        topg_inst.cycle += 1            # adv loop cycle

        if topg_inst.cycle == 6:
            logging.info('do_nice_wait() - EMIT exit trigger' )
            extract_done.set()

    logging.info('do_nice_wait() - Cycle: %s' % topg_inst.cycle )
    logging.info('do_nice_wait() - EXIT thread inst: %s' % topg_inst.yti )

    return      # dont know if this this requireed or good semantics?

def bkgrnd_worker():
    """Threaded wait that does work to build out the 10x10x60 DataFrame"""
    global work_inst
    logging.info('main::bkgrnd_worker() IN Thread - bkgrnd_worker()' )
    logging.info('main::bkgrnd_worker() Ref -> inst #: %s' % work_inst.yti )
    for r in range(4):
        logging.info('main::bkgrnd_worker():: Loop: %s' % r )
        time.sleep(30)    # wait immediatley to let remote update
        work_inst.build_tg_df0()
        work_inst.build_top10()
        work_inst.build_tenten60(r)

    logging.info('main::bkgrnd_worker() EMIT exit trigger' )
    extract_done.set()
    logging.info('main::bkgrnd_worker() EXIT thread inst #: %s' % work_inst.yti )
    return      # dont know if this this requireed or good semantics?


############################# main() ##################################

def main():
    cmi_debug = "aop::"+__name__+"::main()"
    global args
    args = vars(parser.parse_args())        # args as a dict []
    print ( " " )
    print ( "########## Initalizing ##########" )
    print ( " " )
    print ( "CMDLine args:", parser.parse_args() )
    if args['bool_verbose'] is True:        # Logging level
        print ( "Enabeling verbose info logging..." )
        logging.disable(0)                  # Log level = OFF
    else:
        logging.disable(20)                 # Log lvel = INFO

    if args['newsymbol'] is not False:
        print ( " " )
        print ( f"Scanning news for symbol: {args['newsymbol']}" )

    print ( " " )

    recommended = {}        # dict of recomendations

########### 1 - TOP GAINERS ################
    if args['bool_tops'] is True:
        print ( "========== Large Cap / Top Gainers ===============================" )
        ## new JS data extractor
        topgainer_reader = y_cookiemonster(1)         # instantiate class of cookiemonster
        mlx_top_dataset = y_topgainers(1)             # instantiate class
        mlx_top_dataset.init_dummy_session()          # setup cookie jar and headers
 
        mlx_top_dataset.ext_req = topgainer_reader.get_js_data('finance.yahoo.com/markets/stocks/most-active/')
        mlx_top_dataset.ext_get_data(1)

        x = mlx_top_dataset.build_tg_df0()     # build full dataframe
        mlx_top_dataset.build_top10()          # show top 10
        mlx_top_dataset.print_top10()          # print it
        print ( " " )

########### 2 - TOP LOSERS ################
        print ( "========== Large Cap / Top Loosers ================================" )
        ## new JS data extractor
        toploser_reader = y_cookiemonster(2)         # instantiate class of cookiemonster
        mlx_loser_dataset = y_daylosers(1)           # instantiate class
        mlx_loser_dataset.init_dummy_session()       # setup cookie jar and headers
 
        mlx_loser_dataset.ext_req = toploser_reader.get_js_data('finance.yahoo.com/markets/stocks/losers/')
        mlx_loser_dataset.ext_get_data(1)

        x = mlx_loser_dataset.build_tl_df0()     # build full dataframe
        mlx_loser_dataset.build_top10()          # show top 10
        mlx_loser_dataset.print_top10()          # print it
        print ( " " )

########### 3 10x10x60 ################
# **THREAD** waiter
    # do 10x10x60 build-out cycle
    # currently fails to produce a unique data set each threat cycle. Don't know why
    if args['bool_tenten60'] is True:
        print ( "Doing 10x10x60 Gainers loop cycle" )
        logging.info('main() - Doing 10x10x60 thread cycle' )
        global work_inst
        work_inst = y_topgainers(2)
        thread = threading.Thread(target=bkgrnd_worker)    # thread target passes class instance
        logging.info('main() - START thread #1 > 10x10x60 cycler' )
        print ( "Thread loop cycle: ", end="" )
        thread.start()
        while not extract_done.wait(timeout=5):     # wait on thread completd trigger
            print ( ".", end="", flush=True )

        print ( " " )
        # print ( work_inst.tg_df2.sort_values(by=['Symbol','Time'], ascending=True ) )
        print ( work_inst.tg_df2.sort_values(by=['ERank','Time'] ) )

    else:
        print ( " " )

########### Small Cap gainers & loosers ################
# small caps are isolated outside the regular dataset by yahoo.com
    if args['bool_scr'] is True:
        print ( "========== Small Cap / Top Gainers / +5% with Mkt-cap > $299M ==========" )
        scap_reader = y_cookiemonster(2)             # instantiate class of cookiemonster
        small_cap_dataset = smallcap_screen(1)       # instantiate class of a Small Scap Screener
        small_cap_dataset.init_dummy_session()       # setup cookie jar and headers
 
        #small_cap_dataset.get_data(1)
        #small_cap_dataset.ext_req = scap_reader.get_js_data('finance.yahoo.com/screener/predefined/small_cap_gainers/')
        #small_cap_dataset.ext_req = scap_reader.get_js_data('finance.yahoo.com/research-hub/screener/small_cap_gainers/?guccounter=1&guce_referrer=aHR0cHM6Ly9sb2dpbi55YWhvby5jb20v&guce_referrer_sig=AQAAAI3vp_nhrREFAZEd8hz2PmJEWD7VaT_BSBndiFDRmuxRoEdN6B1ueh0ElsNdB6qSP0A-d1sAs_P0_lteTp51lkefa5U4qBxlDDl5HILBDRTJQ9XuGlBvQ-CzUUPSkSF3vyMhxlQnuAaSsrUSJpAZiHIJTy4YcbWJTYz7YRtOm2sH')
        small_cap_dataset.ext_req = scap_reader.get_js_data('finance.yahoo.com/research-hub/screener/small_cap_gainers/')

        small_cap_dataset.ext_get_data(1)
        
        x = small_cap_dataset.build_df0()         # build full dataframe
        small_cap_dataset.build_top10()           # show top 10
        small_cap_dataset.print_top10()           # print it

        #yf_sc_screener = cookie_monster(1, "/screener/predefined/small_cap_gainers/", args)
        #yf_sc_screener.form_url_endpoint()
        #yf_sc_screener.update_headers()
        #yf_sc_screener.init_dummy_session(0)    # 0 = html / 1 = javascript
        #yf_sc_screener.update_cookies()
        #yf_sc_screener.do_html_get()            # jorh = 0
        #yf_sc_screener.update_cookies()
        # jorh : 0 = Simple HTML engine processor / 1 = JAVASCRIPT engine renderer
        #small_cap_dataset.get_data(1, yf_sc_screener.js_resp1, yf_sc_screener.jorh)              # extract data from finance.Yahoo.com

        # Recommendation #1 - Best small cap % gainer with lowest buy-in price
        recommended.update(small_cap_dataset.screener_logic())
        print ( " ")

# process Nasdaq.com unusual_vol ################
    if args['bool_uvol'] is True:
        print ( "========== Unusually high Volume / Up =======================================================" )
        un_vol_activity = un_volumes(1, args)       # instantiate NEW nasdaq data class, args = global var
        un_vol_activity.get_un_vol_data()           # extract JSON data (Up & DOWN) from api.nasdaq.com

        # should test success of extract before attempting DF population
        un_vol_activity.build_df(0)           # 0 = UP Unusual volume
        un_vol_activity.build_df(1)           # 1 = DOWN unusual volume

        # find lowest price stock in unusuall UP volume list
        up_unvols = un_vol_activity.up_unvol_listall()      # temp DF, nicely ordered & indexed of unusual UP vol activity
        ulp = up_unvols['Cur_price'].min()                  # find lowest price row in DF
        uminv = up_unvols['Cur_price'].idxmin()             # get index ID of lowest price row
        u_got_it = up_unvols.loc[uminv]

        ulsym = u_got_it.at['Symbol']              # get symbol of lowest price item @ index_id
        ulname = u_got_it.at['Co_name']            # get name of lowest price item @ index_id
        upct = u_got_it.at['Pct_change']           # get %change of lowest price item @ index_id

        print ( f"Best low-buy OPPTY: #{uminv} - {ulname.rstrip()} ({ulsym.rstrip()}) @ ${ulp} / {upct}% gain" )
        print ( " " )
        print ( f"{un_vol_activity.up_unvol_listall()} " )
        print ( " ")
        print ( "========== Unusually high Volume / Down =====================================================" )
        print ( f"{un_vol_activity.down_unvol_listall()} " )
        print ( " ")
        # Add unusual vol into recommendations list []
        #recommended['2'] = ('Unusual vol:', ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(un_vol_activity.up_df0.loc[uminv, ['Pct_change']][0]) )
        recommended['2'] = ('Unusual vol:', ulsym.rstrip(), '$'+str(ulp), ulname.rstrip(), '+%'+str(upct) )

# generate FINAL combo list ################################################################################
# combine all the findings into 1 place - single source of truth
    """
    DEEP amalysis means - try to understand & inferr plain language reasons as to why these stock are
    appearing in the final 'Single Source of Truth' combo_df. Having a big list of top mover/highly active
    stocks isn't meaningful unless you can understand (quickly in real-time) whats going on with each one.
    From here, you can plan to do something... otherwise, this is just a meaningless list.
    NOTE: Most of this logic prepares/cleans/wrangles data into a perfect combo_df 'Single Source of Truth'.
    """
    if args['bool_deep'] is True and args['bool_scr'] is True and args['bool_uvol'] is True:
        x = combo_logic(1, mlx_top_dataset, small_cap_dataset, un_vol_activity, args )
        x.polish_combo_df(1)
        x.tag_dupes()
        x.tag_uniques()
        x.rank_hot()       # currently disabled b/c it errors. pandas statment needs to be simplifed and split
        #x.find_hottest()
        x.rank_unvol()     # ditto
        x.rank_caps()      # ditto
        x.combo_df.sort_values(by=['Symbol'])         # sort by sumbol name (so dupes are linearly grouped)
        x.reindex_combo_df()                          # re-order a new index (PERMENANT write)

# Summarize combo list key findings ##################################################################
        # Curious Outliers
        # temp_1 = x.combo_df.sort_values(by=['Pct_change'], ascending=False)
        # temp_1 = x.combo_df.sort_values(by=['Symbol'])                        # sort by sumbol name (so dupes are linearly grouped)
        # temp_1.reset_index(inplace=True, drop=True)                           # reset index

        x.find_hottest()

        print ( f"========== Hot stock anomolies ===================================================" )
        if x.combo_dupes_only_listall(1).empty:
            print ( f"NONE found at moment" )
        else:
            print ( f"{x.combo_dupes_only_listall(1)}" )

        print ( " " )
        print ( f"========== Full System of Truth  ===================================================" )
        print ( f"\n{x.combo_df}" )    # sort by %
        print ( " " )

        print ( "========== ** OUTLIERS ** : Unusual UP volume + Top Gainers by +5% ================================" )
        print ( " " )
        temp_1 = x.combo_df.sort_values(by=['Pct_change'], ascending=False) 
        print ( f"{temp_1}" )       # DUPLES in the DF = a curious outlier
        # print ( f"{temp_1[temp_1.duplicated(['Symbol'], keep='first')]}" )    # DUPLES in the DF = a curious outlier
        #print ( f"{temp_1[temp_1.duplicated(['Symbol'], keep='last')]}" )       # DUPLES in the DF = a curious outlier
        print ( " " )
        print ( f"================= >>COMBO<< Full list of intersting market observations ==================" )
        #print ( f"{x.combo_listall_nodupes()}" )
        temp_2 = x.combo_listall_nodupes()                                      # dupes by SYMBOL only
        print ( f"{temp_2.sort_values(by=['Pct_change'], ascending=False)}" )

        if len(x.rx) == 0:      # rx=[] holds hottest stock with lowest price overall
            print ( " " )       # empty list[] = no stock found yet (prob very early in trading morning)
            print ( f"No **hot** stock for >>LOW<< buy-in recommendations list yet" )
        else:
            hotidx = x.rx[0]
            hotsym = x.rx[1]
            hotp = x.combo_df.at[hotidx, 'Cur_price']
            #hotp = x.combo_df.loc[[x.combo_df['Symbol'] == hotsym], ['Cur_price']]
            hotname = x.combo_df.at[hotidx, 'Co_name']
            hotpct = x.combo_df.at[hotidx, 'Pct_change']
            #hotname = x.combo_df.loc[hotidx, ['Co_name']][0]
            print ( " " )       # empty list[] = no stock found yet (prob very early in trading morning)

            #row_index = x.combo_df.loc[x.combo_df['Symbol'] == hotsym.rstrip()].index[0]

            #recommended['3'] = ('Hottest:', hotsym.rstrip(), '$'+str(hotp), hotname.rstrip(), '+%'+str(x.combo_df.loc[hotidx, ['Pct_change']][0]) )
            recommended['3'] = ('Hottest:', hotsym.rstrip(), '$'+str(hotp), hotname.rstrip(), '+%'+str(x.combo_df.at[hotidx, 'Pct_change']) )
            print ( f"==============================================================================================" )
            print ( f"Best low-buy highest %gain **Hot** OPPTY: {hotsym.rstrip()} - {hotname.rstrip()} / {'$'+str(hotp)} / {'+%'+str(hotpct)} gain" )
            print ( " " )
            print ( " " )

        # lowest priced stock
        clp = x.combo_df['Cur_price'].min()
        cminv = x.combo_df['Cur_price'].idxmin()
        i_got_min = x.combo_df.loc[cminv]

        clsym = i_got_min.at['Symbol']                # get symbol of lowest price item @ index_id
        clname = i_got_min.at['Co_name']              # get name of lowest price item @ index_id
        clupct = i_got_min.at['Pct_change']           # get %change of lowest price item @ index_id

        #clsym = x.combo_df.loc[cminv, ['Symbol']][0]
        #clname = x.combo_df.loc[cminv, ['Co_name']][0]    
        #recommended['4'] = ('Large cap:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cminv, ['Pct_change']][0]) )

        recommended['4'] = ('Large cap:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(clupct) )

        # Biggest % gainer stock
        cmax = x.combo_df['Pct_change'].idxmax()
        clp = x.combo_df.loc[cmax, 'Cur_price']
        i_got_max = x.combo_df.loc[cmax]

        clsym = i_got_max.at['Symbol']                # get symbol of lowest price item @ index_id
        clname = i_got_max.at['Co_name']              # get name of lowest price item @ index_id
        clupct = i_got_max.at['Pct_change']           # get %change of lowest price item @ index_id
        #recommended['5'] = ('Top % gainer:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(x.combo_df.loc[cmax, ['Pct_change']][0]) )

        recommended['5'] = ('Top % gainer:', clsym.rstrip(), '$'+str(clp), clname.rstrip(), '+%'+str(clupct) )
        

# Recommendeds ###############################################################
        #  key    recomendation data     - (example output shown)
        # =====================================================================
        #   1:    Small cap % gainer: TXMD $0.818 TherapeuticsMD, Inc. +%7.12
        #   2:    Unusual vol: SPRT $11.17 support.com, Inc. +%26.79
        #   3:    Hottest: AUPH $17.93 Aurinia Pharmaceuticals I +%9.06
        #   4:    Large cap: PHJMF $0.07 PT Hanjaya Mandala Sampoe +%9.2
        #   5:    Top % gainer: SPRT $19.7 support.com, Inc. +%41.12
        # todo: we should do a linear regression on the price curve for each item

        print ( " " )
        print ( f"============ recommendations >>Lowest buy price<< stocks with greatest % gain  =============" )
        print ( " " )
        for k, v in recommended.items():
            print ( f"{k:3}: {v[0]:21} {v[1]:6} {v[3]:28} {v[2]:8} /  {v[4]}" )
            print ( "--------------------------------------------------------------------------------------------" )

# Summary ############### AVERGAES and computed info ##########################
        print ( " " )
        print ( "============== Market activity overview, inisghts & stats =================" )
        avgs_prc = x.combo_grouped(2).round(2)       # insights
        avgs_pct = x.combo_grouped(1).round(2)       # insights

        print ( f"Price average over all stock movemnts" )
        print ( f"{avgs_prc}" )
        print ( " " )
        print ( f"Percent  % average over all stock movemnts" )
        print ( f"{avgs_pct}" )

        #print ( f"Current day average $ gain: ${averages.iloc[-1]['Prc_change'].round(2)}" )
        #print ( f"Current day percent gain:   %{averages.iloc[-1]['Pct_change'].round(2)}" )


# Get the Bull/Bear Technical performance Sentiment for all stocks in combo DF ######################
    """
    Bullish/Neutral/Bearish Technical indicators for each symbol
    Yahoo.com data is inconsistent and randomly unreliable (for Bull/Bear/Neutral state).
    Yahoo wants you to PAY for this info, so they make it difficult to extract.
    """
    if args['bool_te'] is True:
        cmi_debug = __name__+"::Tech_events_all.#1"
        te = y_techevents(1)

        ssot_te = combo_logic(1, mlx_top_dataset, small_cap_dataset, un_vol_activity, args )
        ssot_te.polish_combo_df(1)
        ssot_te.tag_dupes()
        ssot_te.tag_uniques()
        #x.rank_hot()
        #x.rank_unvol()
        #x.rank_caps()
        ssot_te.combo_df.sort_values(by=['Symbol'])         # sort by sumbol name (so dupes are linearly grouped)
        ssot_te.reindex_combo_df()                          # re-order a new index (PERMENANT write)

        print ( f"DEBUG: dump combo_df - {ssot_te}" )
        te.build_te_summary(ssot_te, 1)                     # x = main INSTANCE:: combo_logic
        #
        # TODO: populate build_te_summary with symbol co_name, Cur_price  Prc_change  Pct_change, volume
        # would be good to check if this symbol is also in the UNUSUAL UP table also.
        #     If it is, then add Vol_pct to table also
        #     Also add Index # from main Full Combo table  (make visual lookup quicker/easier)
        #  te_uniques = x.list_uniques()
        print ( f"\n\n" )
        print ( f"========== Hottest stocks Bullish status =============" )
        print ( f"{te.te_df0[['Symbol', 'Today', 'Short', 'Mid', 'Long', 'Bullcount', 'Senti']].sort_values(by=['Bullcount', 'Senti'], ascending=False)}" )
        print ( f"------------------------------------------------------" )
        #
        # HACKING : show uniques from COMBO def
        print ( f"***** Hacking ***** " )
        # might not be necessary now, since I've changed the logic surrounding COMBO DF dupes.
        # c_uniques = x.unique_symbols()
        c_uniques = ssot_te.combo_listall_nodupes()
        te.te_df0.merge(c_uniques, left_on='Symbol', right_on='Symbol')
        # x.combo_listall_nodupes
        print ( f"{te.te_df0}" )
    else:
        pass

# ##### M/L AI News Reader  #########################################################
# ##### Currently read all news or ONE stock
# ###################################################################################

    if args['newsymbol'] is not False:
            cmi_debug = __name__+"::_args_newsymbol.#1"
            news_symbol = str(args['newsymbol'])       # symbol provided on CMDLine
            print ( " " )
            print ( f"M/L news reader for Stock [ {news_symbol} ] =========================" )
            news_ai = ml_nlpreader(1, args)
            sent_ai = ml_sentiment(1, args)
            news_ai.nlp_read_one(news_symbol, args)
            kgraphdb = db_graph(1, args)    # inst a class 
            kgraphdb.con_aopkgdb(1)         # connect to neo4j db

            # check to see if this ticker stmbol exists in KGdb as a Graph node
            # if not, create it
            try:
                found_sym = kgraphdb.check_node_exists(1, news_symbol)
                if found_sym['present'] is True:    # True = symbol already exists
                    created = False
                    pass    # do nothing is Ticker Symbol exists
            except TypeError:
                # Type:class 'NoneType' is discovered here...
                kg_node_id = kgraphdb.create_sym_node(news_symbol)
                created = True

            ttc = 0     # article specific stats : total tokens
            twc = 0     # article specific stats : total words
            tsc = 0     # article specific stats : total scentences / paragra[phs]
            ttkz = 0    # Cumulative : Total Tokens genertaed
            twcz = 0    # Cumulative : Total words read
            tscz = 0    # Cumulative : Total scentences / Paragraphs read

            for sn_idx, sn_row in news_ai.yfn.ml_ingest.items():
                # TESTING code only - to make testing complete quicker (only test 4 docs)
                thint = news_ai.nlp_summary(3, sn_idx)       # what News article TYPE in ml_ingest to look for
                if thint == 0.0:    # only compute type 0.0 prepared and validated new articles in ML_ingest
                    ttc, twc, tsc = news_ai.yfn.extract_article_data(sn_idx, sent_ai)
                    ttkz += ttc
                    twcz += twc
                    tscz += tsc

            print (f"\n\n==================================== Stats ====================================" )
            print (f"Total tokens generated: {ttkz} - Total words read: {twcz} - Total scent/paras read {tscz}" )
            print (f"Human read time: {(twcz / 237):.2f} mins - Total Human processing time: {(twcz / 237) + tscz + (tscz / 2):.2f} mins" )
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            print (f" ==================================== Stats ====================================\n" )

            news_ai.yfn.dump_ml_ingest()

            print (f"{sent_ai.sen_df0}")

            sent_ai.sen_df1 = sent_ai.sen_df0.groupby('Sent').agg(['count'])
            sent_ai.sen_df2 = sent_ai.sen_df0.groupby('Sent')['Rank'].mean()
            sent_ai.sen_df1['Sentiment'] = sent_ai.sen_df2
            sent_ai.sen_df1.loc['Total'] = sent_ai.sen_df1[['Row']].sum()
            print (f"\n")

            neutral_t = sent_ai.sen_df1.loc['Total']['Row']
            sent_ai.sen_df1['Percetage'] = sent_ai.sen_df1['Row'] / neutral_t * 100
            sent_ai.sen_df1 = sent_ai.sen_df1.drop(['Symbol', 'Article', 'Chunk', 'Rank'], axis=1)
            
            #neutral_tt = sent_ai.sen_df1.iloc[3, 0]
            #print ( f"### DEBUG: {neutral_tt}" )

            # number = int(df1.loc[:,'randomcolumn'])
            #sent_ai.sen_df1['Total'] = sent_ai.sen_df0.groupby('Sent').agg(['count']).sum()
            #print ( f"{sent_ai.sen_df0.groupby(['Article', 'Sent'])['Rank'].mean()}" )
            #print ( f"{sent_ai.sen_df0.groupby('Sent').agg(['count'])}" )
            #print ( f"{sent_ai.sen_df0.groupby('Sent')['Rank'].mean()}" )
            #print ( f"### DEBUG 2:\n{neutral_t}" )

            # KGdb stats
            print ( f"{sent_ai.sen_df1}" )
            if created is True:    # True = symbol already exists
                print ( f"Created new KG node_id: {kg_node_id}" )
            else:
                print ( f"Symbol allready exist - New node NOT created !" )
            
            res = kgraphdb.dump_symbols(1)
            kgraphdb.close_aopkgdb(1, kgraphdb.driver)

#################################################################################
# 3 differnt methods to get a live quote ########################################
# NOTE: These 3 routines are *examples* of how to get quotes from the 3 live quote classes::
# TODO: Add a 4th method - via alpaca live API

    """
    EXAMPLE: #1
    nasdaq.com - live quotes via native JSON API test GET
    quote price data is 5 mins delayed
    10 data fields provided
    """

    if args['qsymbol'] is not False:
        nq = nquote(1, args)                          # Nasdqa quote instance from nasdqa_quotes.py
        nq.init_dummy_session()                       # note: this will set nasdaq magic cookie
        nq_symbol = args['qsymbol'].upper()
        logging.info( f"%s - Get Nasdaq.com quote for symbol {nq_symbol}" % cmi_debug )
        nq.update_headers(nq_symbol, "stocks")        # set path: header object. doesnt touch secret nasdaq cookies
        nq.form_api_endpoint(nq_symbol, "stocks")     # set API endpoint url - default GUESS asset_class=stocks
        ac = nq.learn_aclass(nq_symbol)

        if ac != "stocks":
            logging.info( f"%s - re-shape asset class endpoint to: {ac}" % cmi_debug )
            nq.form_api_endpoint(nq_symbol, ac)       # re-form API endpoint if default asset_class guess was wrong)
            nq.get_nquote(nq_symbol.upper())          # get a live quote
            wq = nq_wrangler(1, args)                 # instantiate a class for Quote Data Wrangeling
            wq.asset_class = ac
        else:
            nq.get_nquote(nq_symbol.rstrip())
            wq = nq_wrangler(1, args)                 # instantiate a class for Quote Data Wrangeling
            wq.asset_class = ac                       # wrangeler class MUST know the class of asset its working on

        logging.info( f"============ Getting nasdaq quote data for asset class: {ac} ==========" )
        wq.setup_zones(1, nq.quote_json1, nq.quote_json2, nq.quote_json3)
        wq.do_wrangle()
        wq.clean_cast()
        wq.build_data_sets()
        # add Tech Events Sentiment to quote dict{}
        te_nq_quote = wq.qd_quote
        """
        te = y_techevents(2)
        te.form_api_endpoints(nq_symbol)
        success = te.get_te_zones(2)
        if success == 0:
            te.build_te_data(2)
            te.te_into_nquote(te_nq_quote)
            #nq.quote.update({"today_only": te.te_sentiment[0][2]} )
            #nq.quote.update({"short_term": te.te_sentiment[1][2]} )
            #nq.quote.update({"med_term": te.te_sentiment[2][2]} )
            #nq.quote.update({"long_term": te.te_sentiment[3][2]} )
        else:
            te.te_is_bad()                     # FORCE Tech Events to be N/A
            te.te_into_nquote(te_nq_quote)     # NOTE: needs to be the point to new refactored class nasdqa_wrangler::nq_wrangler qd_quote{}
        """

        print ( f"===================== Nasdaq quote data =======================" )
        print ( f"                          {nq_symbol}" )
        print ( f"===============================================================" )
        c = 1
        for k, v in wq.qd_quote.items():
            print ( f"{c} - {k} : {v}" )
            c += 1
        """
        print ( f"===================== Technial Events =========================" )
        te.build_te_df(1)
        te.reset_te_df0()
        print ( f"{te.te_df0}" )
        print ( f"===============================================================" )
        """

    """
    EXAMPLE #2
    bigcharts.marketwatch.com - data via BS4 scraping
    quote price data is 15 mins delayed
    10 data fields provided
    """
    if args['qsymbol'] is not False:
        bc = bc_quote(5, args)                  # setup an emphemerial dict
        bc_symbol = args['qsymbol'].upper()     # what symbol are we getting a quote for?
        bc.get_basicquote(bc_symbol)            # get the quote
        print ( " " )
        print ( f"Get BIGCharts.com BasicQuote for: {bc_symbol}" )
        print ( f"================= basicquote data =======================" )
        c = 1
        for k, v in bc.quote.items():
            print ( f"{c} - {k} : {v}" )
            c += 1
        print ( f"========================================================" )
        print ( " " )

    """
    EXAMPLE #3
    bigcharts.marketwatch.com - data via BS4 scraping
    quote data is 15 mins delayed
    40 data fields provided
    """
    if args['qsymbol'] is not False:
        bc = bc_quote(5, args)                  # setup an emphemerial dict
        bc_symbol = args['qsymbol'].upper()     # what symbol are we getting a quote for?
        bc.get_quickquote(bc_symbol)            # get the quote
        bc.q_polish()                           # wrangel the data elements
        print ( " " )
        print ( f"Get BIGCharts.com QuickQuote for: {bc_symbol}" )
        print ( f"================= quickquote data =======================" )
        c = 1
        for k, v in bc.quote.items():
            print ( f"{c} - {k} : {v}" )
            c += 1
        print ( f"========================================================" )
        print ( " " )


if __name__ == '__main__':
    main()
