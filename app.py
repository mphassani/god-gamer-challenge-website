import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Load the dataset
file_path = '__THE GOD GAMING CHALLENGE_LOVERS VS THE WORLD - raw data.csv'
data = pd.read_csv(file_path)
# Start the Streamlit app layout
st.set_page_config(page_title="Gaming Challenge Analysis", layout="wide")


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

def Overview():
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
    total_games_df = total_games_df[~total_games_df['Game'].isin(['W', 'L'])]
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

    runs_chart = alt.Chart(games_runs_df).mark_line(point=True, color='red').encode(
        x='Day:O',
        y='Runs:Q',
        tooltip=['Day', 'Runs']
    ).properties(
        title='Runs Per Day'
    )

    # Combining both charts for games played and runs using Altair layering
    combined_chart = alt.layer(runs_chart).resolve_scale(y='independent')
    st.altair_chart(combined_chart, use_container_width=True)

def Games():
    st.title("Game-Specific Stats")
    
    # Dropdown to select a game
    games_list = data.filter(like="Game").apply(pd.Series.value_counts).index.tolist()
    # Filter out 'L' and 'W' from the games list
    games_list = [game for game in games_list if game not in ['L', 'W']]
    # Use the filtered games list in the selectbox
    selected_game = st.selectbox("Select a Game", games_list)

    # Filter data for the selected game
    game_filter = (data.filter(like="Game") == selected_game).any(axis=1)
    game_data = data[game_filter]

    # Data Calculation for the Selected Game
    total_games = len(game_data)
    
    # Counting wins and losses explicitly
    wins = game_data.filter(like="W or L").apply(lambda x: x.str.contains("W", na=False)).sum().sum()
    losses = game_data.filter(like=("W or L")).apply(lambda x: x.str.contains("L", na=False)).sum().sum()

    win_rate = (wins / total_games) * 100 if total_games > 0 else 0

    # Display Calculated Metrics
    st.subheader(f"Stats for {selected_game}")
    st.write(f"**Total Games Played**: {total_games}")
    st.write(f"**Wins**: {wins}")
    st.write(f"**Losses**: {losses}")
    st.write(f"**Win Rate**: {win_rate:.2f}%")

    # Plotting Wins and Losses for the Selected Game using Plotly
    game_win_loss_df = pd.DataFrame({
        'Result': ['Wins', 'Losses'],
        'Count': [wins, losses]
    })

    fig_game_win_loss_pie = px.pie(
        game_win_loss_df, 
        values='Count', 
        names='Result', 
        title=f'Wins vs Losses for {selected_game}',
        color_discrete_sequence=px.colors.qualitative.Set1
    )

    st.plotly_chart(fig_game_win_loss_pie)
    # Calculate Win Streaks for the selected game
    win_streaks = []
    current_streak = 0
    longest_streak = 0
    for result in game_data.filter(like="W or L").values:
        if 'W' in result:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            if current_streak > 0:
                win_streaks.append(current_streak)
            current_streak = 0

    average_streak = sum(win_streaks) / len(win_streaks) if win_streaks else 0

    # Display the streaks
    st.write(f"**Longest Win Streak**: {longest_streak}")
    st.write(f"**Average Win Streak**: {average_streak:.2f}")
    st.write(f"**Current Win Streak**: {current_streak}")

    # Dynamically detect the maximum number of games in the dataset
    game_columns = [col for col in data.columns if col.startswith("Game ") and not col.endswith("W or L")]
    num_games = len(game_columns)  # Number of games (X)

    # Calculate win rate by game position
    position_wins = []
    for i in range(1, num_games + 1):  # Loop through Game 1 to Game X
        # Ensure that W or L values are treated as strings, replacing NaN with empty string
        win_loss_column = data[f"Game {i}: W or L"].fillna("").astype(str)
        
        # Check for wins in the current position
        wins_in_position = (data[f"Game {i}"] == selected_game) & (win_loss_column == 'W')
        
        # Check the total number of times the selected game was played in this position
        total_in_position = (data[f"Game {i}"] == selected_game)
        
        # Calculate win rate
        win_rate = wins_in_position.sum() / total_in_position.sum() if total_in_position.sum() > 0 else 0
        position_wins.append(win_rate)

    # Create a DataFrame to visualize win rate by position
    position_df = pd.DataFrame({
        'Position': range(1, num_games + 1),
        'Win Rate': position_wins
    })

    # Plot the win rate by position using Altair
    position_chart = alt.Chart(position_df).mark_bar().encode(
        x='Position:O',
        y='Win Rate:Q',
        tooltip=['Position', 'Win Rate']
    ).properties(title=f'Win Rate by Position for {selected_game}')
    st.altair_chart(position_chart, use_container_width=True)

    # Calculate how many more games are played after playing the selected game in each run
    games_after = []
    for i in range(1, num_games):  # Loop through Game 1 to Game X-1
        # Check if Game i+1 exists and is not NaN
        played_after = data.loc[(data[f"Game {i}"] == selected_game), f"Game {i+1}: W or L"].notna().sum()
        games_after.append(played_after)

    # Dynamically detect the maximum number of games in the dataset
    game_columns = [col for col in data.columns if col.startswith("Game ") and not col.endswith("W or L")]
    num_games = len(game_columns)  # Number of games (X)

    # Create a list to store the number of games played after for each turn and position in the run
    games_after_data = []

    # Loop through each row to determine how many games were played after each occurrence of the selected game
    for index, row in data.iterrows():
        for i in range(1, num_games):  # Loop through Game 1 to Game X-1
            # Check if the selected game was played in this position
            if row[f"Game {i}"] == selected_game:
                # Calculate how many more games were played after this occurrence of the selected game
                games_after = data.loc[index, f"Game {i+1}: W or L":f"Game {num_games}: W or L"].notna().sum()
                
                # Store the result as turn and position
                games_after_data.append({
                    'Turn': i,
                    'Games Played After': games_after,
                    'Run': row['Run'] if 'Run' in row else index  # Using 'Run' if available, otherwise use index
                })

    # Convert the results to a DataFrame
    games_after_df = pd.DataFrame(games_after_data)

    # Group the data by turn and calculate the average games played after for each turn
    avg_games_after_by_turn = games_after_df.groupby('Turn')['Games Played After'].mean().reset_index()

    # Plot the average games played after the selected game by turn using Altair
    games_after_chart = alt.Chart(avg_games_after_by_turn).mark_bar().encode(
        x='Turn:O',
        y='Games Played After:Q',
        tooltip=['Turn', 'Games Played After']
    ).properties(title=f'Average Games Played After Each Turn for {selected_game}')
    st.altair_chart(games_after_chart, use_container_width=True)

    # Display the average number of games played after by position in the run
    st.write(f"**Average Games Played After Playing {selected_game} by Turn**")
    st.dataframe(avg_games_after_by_turn)

page = st.navigation([st.Page(Overview), st.Page(Games)])
page.run()