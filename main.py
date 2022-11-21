import streamlit as st
import pandas as pd

#---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(page_title='The MatchUp AI App Developed by Vinny',
    layout='wide')

#---------------------------------#
# Model building

#---------------------------------#
st.write("""
# The MatchUp AI App Developed by Vinny
In this implementation, Random Forest Algorithm and Neural Network build on 2008 - 2022 Historical cricket data to build a classification model using the **Machine Leaning** algorithm.
""")

def batsmen_bowler_present(batsman_name,bowler_name):
    """Used to check if the given names are valid or not"""
    batsman_present=False
    bowler_present=False
    # Checking whether the name is correct by matching it with all batsman,bowler unique names
    if batsman_name in list(runs_balls_played_whole['batsman'].unique()) and bowler_name in list(bowler_statistics_whole['bowler'].unique()):
        return True
    
def dataframe_info_sender(batsman_name,bowler_name):
    """Sending dataframes of the given batsman and bowler"""
    batsman_whole=runs_balls_played_whole[runs_balls_played_whole['batsman']==batsman_name]
    batsman_danger=batsman_statistics_danger[batsman_statistics_danger['batsman']==batsman_name]
    bowler_whole=bowler_statistics_whole[bowler_statistics_whole['bowler']==bowler_name]
    bowler_danger=bowler_stats_danger[bowler_stats_danger['bowler']==bowler_name]
    return (batsman_whole,batsman_danger,bowler_whole,bowler_danger)

def compare(batsman_name,bowler_name):
    """compare(batsman_name,bowler_name) function let's you compare a batsman and a bowler and then prints who is a better
    T20 player. The result depends upon the players strike rate/ economy in all 20 overs,
    and specially the performance of a player in the dangerous overs."""
    # Checking if names are valid and can be compared
    # condition for comparing is both the given names must have played more than 200 balls.
    if batsmen_bowler_present(batsman_name,bowler_name):
        
        # Getting the info related to the given names
        
        batsman_whole,batsman_danger,bowler_whole,bowler_danger = dataframe_info_sender(batsman_name,bowler_name)
        st.write(batsman_whole)
        st.write(bowler_whole)
        
        # The below variables are used to know whether batsman and bowler are in the top 10 list of danger overs
        
        bat_dang_length = len(batsman_danger) 
        bowl_dang_length = len(bowler_danger)
        
        # result_bat and result_bowl are used to give points to the batsman or bowler if he is found to be a better 
        # player with the given below conditions.
        
        result_bat = 0
        result_bowl = 0
        
        # Checking for better player in all 20 overs using z scores
        
        if batsman_whole['z'].values[0] > bowler_whole['z'].values[0]:
            result_bat=result_bat+1
            
        elif batsman_whole['z'].values[0] < bowler_whole['z'].values[0]:
            result_bowl=result_bowl+1
            
        elif batsman_whole['z'].values[0] == bowler_whole['z'].values[0]:
            result_bat=result_bat+1
            result_bowl=result_bowl+1
            
        # Checking for better player in dangerous overs using z score
        
        # If both bowler and batsman are in top 10 list of danger over players with high strike rate/econ.
        
        if bat_dang_length > 0 and bowl_dang_length > 0:
            if batsman_danger['z'].values[0] > bowler_danger['z'].values[0]:
                result_bat+=1
                
            elif batsman_danger['z'].values[0] < bowler_danger['z'].values[0]:
                result_bowl+=1
                
            elif batsman_danger['z'].values[0] == bowler_danger['z'].values[0]:
                result_bat+=1
                result_bowl+=1
                
        # If the given batsman is in the top 10 list of danger overs and bowler isn't        
        
        elif bat_dang_length == 0 and bowl_dang_length > 0:
            result_bowl+=2
            
        # If the given batsman is not in top 10 list and bowler is    
        
        elif bat_dang_length > 0 and bowl_dang_length == 0:
            result_bat+=2
            
        # Comparing points given in above condition and printing result    
        
        if result_bat > result_bowl:
            st.write(batsman_name,'will over power ',bowler_name,'if match played today')
        elif result_bat < result_bowl:
            st.write(bowler_name,'will over power ',batsman_name,'if match played today')
        elif result_bat == result_bowl:
            st.write(batsman_name,'and',bowler_name,'are of same level it would be equal fight')
    else:
        
        # If batsman/bowler are not valid names or they aren't comparable because of not played more than 200 balls. 
        
        st.write('Sorry, either your player names are incorrect or they haven\'t played more than 200 balls in T20',end='')
        st.write('. Thus are not comparable.')
        
data=pd.read_csv('deliveries.csv')
ipl=pd.read_csv('matches.csv')
merged=ipl.merge(data,left_on='id',right_on='match_id')
total_runs=merged.groupby('batsman')['batsman_runs'].sum().reset_index()
balls_played=merged.groupby('batsman')['batsman_runs'].count().reset_index()
runs_balls_played_whole=total_runs.merge(balls_played,on='batsman')
runs_balls_played_whole.rename(columns={'batsman_runs_y':'balls_played','batsman_runs_x':'runs'},inplace=True)

runs_balls_played_whole['strike']=(runs_balls_played_whole['runs']/runs_balls_played_whole['balls_played'])*100

runs_balls_played_whole=runs_balls_played_whole[runs_balls_played_whole['balls_played']>=200]


mean_bat_whole=runs_balls_played_whole['strike'].mean()
std_bat_whole=runs_balls_played_whole['strike'].std()
runs_balls_played_whole['z']=(runs_balls_played_whole['strike']-mean_bat_whole)/std_bat_whole

bowlers=merged.copy()
dismissal=['caught','bowled','lbw','stumped','caught and bowled','hit wicket']
total_wickets=bowlers[bowlers['dismissal_kind'].isin(dismissal)]

total_wickets=total_wickets.groupby('bowler')['player_dismissed'].count().sort_values(ascending=False).reset_index()
total_wickets.rename(columns={'player_dismissed':'wickets'},inplace=True)

runs_given=bowlers.groupby('bowler')['total_runs'].sum().reset_index()
runs_given.rename(columns={'total_runs':'runs'},inplace=True)

balls_bowled=bowlers.groupby('bowler')['total_runs'].count().reset_index()
balls_bowled.rename(columns={'total_runs':'balls_bowled'},inplace=True)

bowler_statistics_whole=total_wickets.merge(runs_given,on='bowler')
bowler_statistics_whole=bowler_statistics_whole.merge(balls_bowled,on='bowler')

bowler_statistics_whole['econ']=100-(bowler_statistics_whole['runs']/(bowler_statistics_whole['balls_bowled']/6))

bowler_statistics_whole=bowler_statistics_whole[bowler_statistics_whole['balls_bowled']>=200]

mean_bowl_whole=bowler_statistics_whole['econ'].mean()
std_bowl_whole=bowler_statistics_whole['econ'].std()

bowler_statistics_whole['z']=(bowler_statistics_whole['econ']-mean_bowl_whole)/std_bowl_whole

mask=merged['over']>15
danger=merged[mask]

total_runs_danger=danger.groupby('batsman')['batsman_runs'].sum().reset_index()
total_runs_danger.rename(columns={'batsman_runs':'runs'},inplace=True)
total_balls_danger=danger.groupby('batsman')['batsman_runs'].count().reset_index()
total_balls_danger.rename(columns={'batsman_runs':'balls'},inplace=True)
batsman_statistics_danger=total_runs_danger.merge(total_balls_danger,on='batsman')
batsman_statistics_danger=batsman_statistics_danger[batsman_statistics_danger['balls']>=200]
batsman_statistics_danger['strike']=(batsman_statistics_danger['runs']/batsman_statistics_danger['balls'])*100

mean_bat_danger=batsman_statistics_danger['strike'].mean()
std_bat_danger=batsman_statistics_danger['strike'].std()

batsman_statistics_danger['z']=(batsman_statistics_danger['strike']-mean_bat_danger)/std_bat_danger

batsman_statistics_danger=batsman_statistics_danger.sort_values('z',ascending=False).head(10)


total_runs_given_dang=danger.groupby('bowler')['total_runs'].sum().reset_index()
total_runs_given_dang.rename(columns={'total_runs':'runs'},inplace=True)
total_balls_dang=danger.groupby('bowler')['total_runs'].count().reset_index()
total_balls_dang.rename(columns={'total_runs':'balls'},inplace=True)
bowler_stats_danger=total_runs_given_dang.merge(total_balls_dang,on='bowler')
bowler_stats_danger=bowler_stats_danger[bowler_stats_danger['balls']>=200]
bowler_stats_danger['econ']=100-(bowler_stats_danger['runs']/(bowler_stats_danger['balls']/6))

mean_bowl_dang=bowler_stats_danger['econ'].mean()
std_bowl_dang=bowler_stats_danger['econ'].std()

bowler_stats_danger['z']=(bowler_stats_danger['econ']-mean_bowl_dang)/std_bowl_dang

bowler_stats_danger=bowler_stats_danger.sort_values('z',ascending=False).head(10)

runs_balls_played_whole=runs_balls_played_whole[runs_balls_played_whole['balls_played']>=200]
x=runs_balls_played_whole['batsman'].to_list()
option1 = st.selectbox("Select a batsmen?",x,label_visibility="hidden",)

bowler_statistics_whole=bowler_statistics_whole[bowler_statistics_whole['balls_bowled']>=200]
y=bowler_statistics_whole['bowler'].to_list()
option2 = st.selectbox("Select a batsmen?",x,label_visibility="hidden",key='vinny')

if st.button('Predict Match-Up'):
    compare(option1,option2)
