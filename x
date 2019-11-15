
# note: Pandas DataFrame = allfixtures.ds_df0 - allready pre-initalized as EMPYT on __init__
        ds_data0 = [[ \
                    self.gt, \
                    self.team_h, \
                    home_team, \
                    away_team, \
                    self.team_a, \
                    abs(ranking_mismatch), \
                    abs(goal_diff_delta), \
                    abs(gf_delta), \
                    ga_delta, \
                    h_win_prob, \
                    a_win_prob, \
                    h_win, \
                    round(self.hga, 2), \
                    game_weight, \
                    abs( round(playme, 1) ) ]]

        df_temp0 = pd.DataFrame(ds_data0, \
                    columns=[ \
                    'Time', 'Hid', 'Home', 'Away', 'Aid', \
                    'RankD', 'GDd', 'GFd', 'GAd', 'Hwin', \
                    'Awin', 'HomeA', 'HGA', 'Weight', 'PlayME' ], \
                    index=[game_tag] )

        allfixtures.ds_df0 = allfixtures.ds_df0.append(df_temp0)    # append this ROW of data into the DataFrame
		
