
# Pandad dataframe code example
#   - to compute Analytics and insert results as new colum of existing DataFrame


else:
    ds_hm_df5 = pd.DataFrame()
    print ( " " )
    print ( "========================= Deep squad analytics for my active squad ===========================" )
    print ( "=========================", fav_league.my_leaguename(), "", end="" )
    for P in range(67 - len(fav_league.my_leaguename()) ):
        print ( "=", end="" )
        # pretty print leaderboard title
    print ( " " )
    for pos in range (0, 15):
        ds_hm_data0 = []
        opp_team_id = []
        opp_team_name = []
        #print ( "Player:", pos+1, " ", end="" )
        got_him = my_priv_data.get_oneplayer(pos)    # cycle trhough all players on MY TEAM - WARNING: prints out some info also
        for oid, i in opp_team_inst.items():         # cycle through cached class instances of each OPPONENTS team
            if oid != int(i_am.playeridnum):         # skip *my team* in the cached class instances
                found_him = i.got_player(got_him)    # does this player exists in this OPPONENTS squad
                if found_him == 1:                   # returns 1 if this player exists in this squad
                    x = scan_pe_cache(pe_inst_cache, oid)   # get pe_inst from pre-populated player entry instance cache
                    y = x.my_teamname()
                    opp_team_id.append(x.my_id())
                    opp_team_name.append(x.my_teamname())
                    ds_hm_data0.append(1)
                else:
                    ds_hm_data0.append(0)
                    x = scan_pe_cache(pe_inst_cache, oid)   # get pe_inst from pre-populated player entry instance cache
                    opp_team_id.append(x.my_id())
                    opp_team_name.append(x.my_teamname())
                    pass
        # COLUMN total logic
        ds_hm_data3 = (pd.Series(ds_hm_data0, index=opp_team_name) )       # setup a series as data for COLUMN insertion
        ds_hm_df5.insert(loc=0, value=ds_hm_data3, column=got_him )        # inset COLUMN
    # create new ROW of COLUMN totals
    hm_tr_data0 = pd.Series( ds_hm_df5.sum(axis=0), name='X-ref TOTALS' )   # setup new ROW = count of COLUMN totals
    ds_hm_df5 = ds_hm_df5.append(hm_tr_data0)    # append this ROW into existing DataFrame as FINAL row
    # ROW total logic
    new_col = pd.DataFrame(ds_hm_df5.sum(axis=1))    # compute ROW totals for ouput as a new COLUMN
    # create new COLUMN of ROW totals
    ds_hm_df5 = ds_hm_df5.assign( TOTAL=new_col )    # add new ROW into existing DataFrame
    print ( ds_hm_df5 )
    print ( "==============================================================================================" )
