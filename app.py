import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Load the dataset
file_path = '__THE GOD GAMING CHALLENGE_LOVERS VS THE WORLD - raw data.csv'
data = pd.read_csv(file_path)

# Prepare the data
games_per_day = data.groupby("Day").size()
wins_per_day = data.filter(like="W or L").apply(lambda x: x.str.count("W")).sum(axis=1)
total_wins = data.filter(like="W or L").apply(lambda x: x.str.count("W")).sum().sum()
total_losses = data.filter(like="W or L").apply(lambda x: x.str.count("L")).sum().sum()

win_loss_ratio = data.groupby("Day").apply(lambda x: x.filter(like="W or L").apply(lambda x: x.str.count("W")).sum().sum() / (x.filter(like="W or L").apply(lambda x: x.str.count("L")).sum().sum() + 1))
first_games = data["Game 1"].value_counts().nlargest(5)
first_game_results = data.groupby("Game 1")["Game 1: W or L"].value_counts(normalize=True).unstack().fillna(0)
top_5_first_games = first_game_results.loc[first_games.index].reset_index()

total_games_played = data.filter(like="Game").apply(pd.Series.value_counts).fillna(0).sum(axis=1).sort_values(ascending=False)
games_per_day = data.groupby("Day").apply(lambda x: x.filter(like="Game").notnull().sum().sum())
runs_per_day = data.groupby("Day").size()

# Start the Streamlit app layout
st.set_page_config(page_title="Gaming Challenge Analysis", layout="wide")

st.title("The God Gaming Challenge: Analysis & Strategy")
st.write("Hey guys, I used u/readalot2 data to create something a bit more visual and interactive. Hope you enjoy and if you have any data ideas let me know I can cook it up quick! I can also link it directly to the sheet so the data updates as new data is entered but I'm working on it.")

# Section 1: Win/Loss Ratio Per Day using Altair
st.subheader("Win/Loss Ratio Over Time")
win_loss_df = pd.DataFrame({
    'Day': win_loss_ratio.index,
    'Win/Loss Ratio': win_loss_ratio.values
})

win_loss_chart = alt.Chart(win_loss_df).mark_line(point=True).encode(
    x='Day:O',
    y='Win/Loss Ratio:Q',
    tooltip=['Day', 'Win/Loss Ratio']
).properties(
    title='Win/Loss Ratio Per Day'
)

# Layout with Altair win/loss ratio and first game win/lose percentage side by side
col1, col2 = st.columns(2)

with col1:
    st.altair_chart(win_loss_chart, use_container_width=True)

# Section 2: Top 5 First Games Win vs. Lose Percentage using Altair
top_5_df = top_5_first_games.melt(id_vars=['Game 1'], value_vars=['W', 'L'], var_name='Result', value_name='Percentage')

first_games_chart = alt.Chart(top_5_df).mark_bar().encode(
    x='Game 1:N',
    y='Percentage:Q',
    color='Result:N',
    tooltip=['Game 1', 'Result', 'Percentage']
).properties(
    title='Top 5 First Games: Win vs Lose Percentage'
)

with col2:
    st.altair_chart(first_games_chart, use_container_width=True)

# Section 3: Wins vs Losses and Percentage of Total Games Played using Plotly
st.subheader("Wins vs. Losses and Game Distribution")

# Create pie chart data
win_loss_pie_data = pd.DataFrame({
    'Result': ['Wins', 'Losses'],
    'Count': [total_wins, total_losses]
})

# Pie chart for Wins vs Losses
fig_win_loss_pie = px.pie(win_loss_pie_data, values='Count', names='Result', title='Total Wins vs. Losses', color_discrete_sequence=px.colors.qualitative.Set1)

# Pie chart for Percentage of Total Games Played
total_games_df = pd.DataFrame({
    'Game': total_games_played.index,
    'Count': total_games_played.values
})
fig_game_pie = px.pie(total_games_df, values='Count', names='Game', title='Percentage of Total Games Played', color_discrete_sequence=px.colors.qualitative.Set3)

# Display the two pie charts side by side
col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(fig_win_loss_pie, use_container_width=True)

with col4:
    st.plotly_chart(fig_game_pie, use_container_width=True)

# Section 4: Games Played and Runs Per Day using Altair
st.subheader("Daily Game Activity")
games_runs_df = pd.DataFrame({
    'Day': games_per_day.index,
    'Games Played': games_per_day.values,
    'Runs': runs_per_day.values
})

games_played_chart = alt.Chart(games_runs_df).mark_line(point=True, color='blue').encode(
    x='Day:O',
    y='Games Played:Q',
    tooltip=['Day', 'Games Played']
).properties(
    title='Games Played Per Day'
)

runs_chart = alt.Chart(games_runs_df).mark_line(point=True, color='red').encode(
    x='Day:O',
    y='Runs:Q',
    tooltip=['Day', 'Runs']
).properties(
    title='Runs Per Day'
)

# Combining both charts for games played and runs using Altair layering
combined_chart = alt.layer(games_played_chart, runs_chart).resolve_scale(y='independent')
st.altair_chart(combined_chart, use_container_width=True)