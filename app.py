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

total_games_played = data.filter(like="Game").apply(lambda x: x[~x.isin(['W', 'L'])].value_counts()).fillna(0).sum(axis=1).sort_values(ascending=False)
games_per_day = data.groupby("Day").apply(lambda x: x.filter(like="Game").notnull().sum().sum())
runs_per_day = data.groupby("Day").size()
# Dropdown to select a game
games_list = data.filter(like="Game").apply(pd.Series.value_counts).index.tolist()
# Filter out 'L' and 'W' from the games list
games_list = [game for game in games_list if game not in ['L', 'W']]

# Function to calculate overall daily win rates
def calculate_daily_total_win_rates(data):
    win_loss_columns = [col for col in data.columns if col.endswith("W or L")]
    daily_total_win_rates = []

    for day, group in data.groupby('Day'):
        total_games = 0
        total_wins = 0
        for col in win_loss_columns:
            game_data = group[col].dropna()
            total_games += len(game_data)
            total_wins += game_data.str.contains("W").sum()
        
        win_rate = (total_wins / total_games) * 100 if total_games > 0 else 0
        daily_total_win_rates.append({'Day': day, 'Total Win Rate': win_rate})
    
    return pd.DataFrame(daily_total_win_rates)

# Calculate overall daily win rates
daily_total_win_rates = calculate_daily_total_win_rates(data)

def calculate_daily_game_win_rates(data):
    win_rates_by_game = {}
    
    game_columns = [col for col in data.columns if col.startswith("Game ") and not col.endswith("W or L")]
    win_loss_columns = [col for col in data.columns if col.endswith("W or L")]
    
    for game_col, win_loss_col in zip(game_columns, win_loss_columns):
        daily_win_rates = []
        for day, group in data.groupby('Day'):
            game_data = group[[game_col, win_loss_col]].dropna()
            total_games = len(game_data)
            wins = game_data[win_loss_col].str.contains("W").sum()
            win_rate = (wins / total_games) * 100 if total_games > 0 else 0
            daily_win_rates.append({'Day': day, 'Win Rate': win_rate})
        win_rates_by_game[game_col] = pd.DataFrame(daily_win_rates)
    return win_rates_by_game

# Calculate daily game win rates
win_rates_by_game = calculate_daily_game_win_rates(data)
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
        x=alt.X('Day:O', axis=alt.Axis(labelAngle=0)),
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
    fig_win_loss_pie = px.pie(win_loss_pie_data, values='Count', names='Result', title='Total Wins vs. Losses', color_discrete_sequence=["#2B66A4","#DB0016"])

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

    # Section 5: Average win rate per game displayed in a bar chart
    st.subheader("Average Win Rate Per Game")

    # Initialize a dictionary to store the total wins, losses, and win rates for each game
    game_win_rates = {}

    # Loop through each game in the games list
    for game in games_list:
        wins = 0
        losses = 0
        
        # Filter the rows where the selected game is played
        for i in range(len(games_list)):
            game_column = f"Game {i+1}"
            win_loss_column = f"Game {i+1}: W or L"
            
            if game_column in data.columns and win_loss_column in data.columns:
                # Only consider rows where the current game is in the 'Game' column
                game_rows = data[game_column] == game
                win_loss_data = data.loc[game_rows, win_loss_column]
                
                # Count wins and losses for the current game
                wins += win_loss_data.str.contains('W', na=False).sum()
                losses += win_loss_data.str.contains('L', na=False).sum()

        # Calculate total games and win rate for this game
        total_games = wins + losses
        win_rate = (wins / total_games) * 100 if total_games > 0 else 0
        
        # Store the win rate for the current game
        game_win_rates[game] = win_rate

    # Convert the win rates to a DataFrame for visualization
    win_rate_df = pd.DataFrame({
        'Game': list(game_win_rates.keys()),
        'Win Rate': list(game_win_rates.values())
    })

    # Create the bar chart using Altair
    win_rate_chart = alt.Chart(win_rate_df).mark_bar().encode(
        x='Game:N',
        y='Win Rate:Q',
        tooltip=['Game', 'Win Rate']
    ).properties(
        title='Average Win Rate Per Game'
    )

    # Display the chart
    win_rate_chart = win_rate_chart.encode(
        x=alt.X('Game:N', sort=alt.EncodingSortField(field='Win Rate', order='ascending'))
    )
    st.altair_chart(win_rate_chart, use_container_width=True)


    # Calculate the minimum value for the y-axis to avoid starting from 0
    min_win_rate = daily_total_win_rates['Total Win Rate'].min()

    # Create the base chart
    total_win_rate_chart = alt.Chart(daily_total_win_rates).mark_line(point=True).encode(
        x=alt.X('Day:O', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Total Win Rate:Q', scale=alt.Scale(domain=[min_win_rate, daily_total_win_rates['Total Win Rate'].max()])),
        tooltip=['Day', 'Total Win Rate']
    ).properties(
        title='Total Win Rate Per Day for All Games'
    )
 
    # Calculate the average win rate
    average_win_rate = total_win_rate_chart.transform_regression('Day', 'Total Win Rate').mark_line(color='red', strokeDash=[5, 5])

    # Combine the win rate chart and the average trend line
    combined_chart = total_win_rate_chart + average_win_rate

    # Display the chart
    st.altair_chart(combined_chart, use_container_width=True)

    # Section 4: Games Played and Runs Per Day using Altair
    st.subheader("Daily Game Activity")
    games_runs_df = pd.DataFrame({
        'Day': games_per_day.index,
        'Games Played': games_per_day.values,
        'Runs': runs_per_day.values
    })

    runs_chart = alt.Chart(games_runs_df).mark_line(point=True, color='red').encode(
        x=alt.X('Day:O', axis=alt.Axis(labelAngle=0)),
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

    # Use the filtered games list in the selectbox
    selected_game = st.selectbox("Select a Game", games_list)

    # Filter the rows where the selected game is played
    game_filter = (data.filter(like="Game") == selected_game)

    # Initialize win and loss counters
    wins = 0
    losses = 0

    # Loop through each 'Game X' column and its corresponding 'W or L' column
    for i in range(len(game_filter.columns)):
        game_column = f"Game {i+1}"
        win_loss_column = f"Game {i+1}: W or L"

        if game_column in data.columns and win_loss_column in data.columns:
            # Only consider rows where the selected game is in the 'Game' column
            game_rows = data[game_column] == selected_game
            win_loss_data = data.loc[game_rows, win_loss_column]

            # Count wins and losses in the filtered rows
            wins += win_loss_data.str.contains('W', na=False).sum()
            losses += win_loss_data.str.contains('L', na=False).sum()

    # Calculate total games played
    total_games = wins + losses

    # Calculate win rate
    win_rate = (wins / total_games) * 100 if total_games > 0 else 0

    # Use two columns for the stats
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Stats for {selected_game}")
        st.write(f"**Total Games Played**: {total_games}")
        st.write(f"**Wins**: {wins}")
        st.write(f"**Losses**: {losses}")
        st.write(f"**Win Rate**: {win_rate:.2f}%")

        # Calculate Win Streaks for the selected game
        win_streaks = []
        current_streak = 0
        longest_streak = 0

        for i in range(len(game_filter.columns)):
            win_loss_column = f"Game {i+1}: W or L"

            if win_loss_column in data.columns:
                for result in data[win_loss_column].dropna():
                    if result == 'W':  # Ensure you're comparing the specific result
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

    with col2:
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
            color_discrete_sequence=["#2B66A4","#DB0016"],
            width=400,  # Adjusted size to make it smaller
            height=300
        )
        st.plotly_chart(fig_game_win_loss_pie, use_container_width=True)

    # Dynamically detect the maximum number of games in the dataset
    game_columns = [col for col in data.columns if col.startswith("Game ") and not col.endswith("W or L")]
    num_games = len(game_columns)  # Number of games (X)

    #Section to show the daily win rate for the selected game
    st.subheader(f"Daily Win Rate for {selected_game}")

    # Calculate win rate by game position
    position_wins = []
    for i in range(1, num_games + 1):  # Loop through Game 1 to Game X
        win_loss_column = data[f"Game {i}: W or L"].fillna("").astype(str)
        wins_in_position = (data[f"Game {i}"] == selected_game) & (win_loss_column == 'W')
        total_in_position = (data[f"Game {i}"] == selected_game)
        win_rate = wins_in_position.sum() / total_in_position.sum() if total_in_position.sum() > 0 else 0
        position_wins.append(win_rate)

    # Filter the relevant columns that contain game names and their respective win/loss columns
    game_columns = [col for col in data.columns if 'Game' in col]
    win_loss_columns = [col for col in data.columns if 'W or L' in col]

    # Prepare a list to store win/loss data for the selected game
    filtered_data = []

    # Iterate through the data and filter out the results for the selected game
    for index, row in data.iterrows():
        for i in range(1, 11):  # There are up to 10 games and win/loss columns
            game_col = f'Game {i}'
            win_loss_col = f'Game {i}: W or L'
            
            if game_col in row and isinstance(row[game_col], str) and selected_game in row[game_col]:
                if win_loss_col in row:
                    filtered_data.append({'Day': row['Day'], 'Win/Loss': row[win_loss_col]})

    # Convert filtered data into a DataFrame
    filtered_df = pd.DataFrame(filtered_data)

    # Remove rows where the win/loss information is NaN
    filtered_df = filtered_df.dropna()

    # Calculate win rate by grouping by 'Day' and calculating the percentage of 'W' (win) for each day
    win_rate_for_game_given_day = filtered_df.groupby('Day').apply(lambda x: (x['Win/Loss'] == 'W').mean() * 100).reset_index(name='Win Rate')

    # Plot the win rate using Altair
    win_rate_per_game_per_day = alt.Chart(win_rate_for_game_given_day).mark_bar().encode(
        x=alt.X('Day:N', title='Day'),
        y=alt.Y('Win Rate:Q', title='Win Rate (%)')
    ).properties(
        title=f'Win Rate for {selected_game} per Day',
        width=600,
        height=400
    )
    # chart_with_trendline = chart + chart.transform_regression('Day', 'Win Rate').mark_line(color='red',strokeDash=[5, 5])
    st.altair_chart(win_rate_per_game_per_day, use_container_width=True)
        
    # Create a DataFrame to visualize win rate by position
    position_df = pd.DataFrame({
        'Position': range(1, num_games + 1),
        'Win Rate': position_wins
    })

    # Plot the win rate by position using Altair
    position_chart = alt.Chart(position_df).mark_bar().encode(
        x=alt.X('Position:O', axis=alt.Axis(labelAngle=0)),
        y='Win Rate:Q',
        tooltip=['Position', 'Win Rate']
    ).properties(title=f'Win Rate by Position for {selected_game}')
    st.altair_chart(position_chart, use_container_width=True)


page = st.navigation([st.Page(Overview), st.Page(Games)]) 
page.run()