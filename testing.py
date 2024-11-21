import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox

def fetch_data(week):
    year = 2024
    league_id = "1821897649"
    swid = "{9A7CC82B-E2EF-4BC6-A945-03355F0551BA}"
    espn_s2 = "AECy9hVogBZqVHEf%2FRRb8EN%2BbsHrkLEBB1o4mrzFE67BmNOF6F%2B9WyRDv6IejeljCXULm6wATwskH3F7qs0LssX8ZYhwlZG7gt%2FuKkv%2ByTv4EkMgErZOHDo02j0QdhvDat6rtR0ITQ3utT%2FsSq4NHXLpquCP1ZuM9hcnurtcp%2F%2FIy5LqLiyoEOl9yU%2FJLfHKDpWVnhYOFHd4xOmMLgxu3si7D8rJMnyrB92kIYz1XhXo8rdci7unqx6O1lgB3UvL4F%2BxjaakdWp15kr9rMvW3n2znai%2FQ6ZKdSjujUTlUss3uZ4I6L1nHu2%2BM3sgpm2a2rDMtFhu8fIvK%2Bg8jnFsnlKw"
    url = 'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{}/segments/0/leagues/{}?scoringPeriodId={}&view=mBoxscore&view=mMatchupScore&view=mRoster&view=mSettings&view=mStatus&view=mTeam&view=modular&view=mNav'.format(year, league_id, week)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://fantasy.espn.com/',
        'Origin': 'https://fantasy.espn.com',
        'x-fantasy-filter': f'{{"schedule":{{"filterMatchupPeriodIds":{{"value":[{week}]}}}}}}',
        'x-fantasy-platform': 'kona-PROD-c495d34b311913252eb42e5284fe45c2a8cfbdc5',
        'x-fantasy-source': 'kona'
    }

    cookies = {
        "SWID": swid,
        "espn_s2": espn_s2
    }

    r = requests.get(url, headers=headers, cookies=cookies)
    r.raise_for_status()  # Check for HTTP errors

    data = r.json()

    # Create a dictionary to map teamId to team details
    team_map = {team['id']: team for team in data['teams']}

    matchups = []
    home_scores = []
    away_scores = []
    winners = []

    # Extract and print the total points scored by each team
    for matchup in data['schedule']:
        home_team_id = matchup['home']['teamId']
        home_score = matchup['home']['totalPoints']
        away_team_id = matchup['away']['teamId']
        away_score = matchup['away']['totalPoints']

        home_team_name = team_map[home_team_id]['name']
        away_team_name = team_map[away_team_id]['name']

        matchups.append(f"{home_team_name} vs {away_team_name}")
        home_scores.append(home_score)
        away_scores.append(away_score)

        if home_score > away_score:
            winners.append((home_team_name, away_team_name, home_team_name))
        else:
            winners.append((home_team_name, away_team_name, away_team_name))

    return matchups, home_scores, away_scores, winners

def plot_data(week):
    try:
        week = int(week)
        if week < 1 or week > 10:
            raise ValueError("Week must be between 1 and 10.")
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))
        return

    matchups, home_scores, away_scores, winners = fetch_data(week)

    fig, ax = plt.subplots(figsize=(8, 5))  # Decrease the figure size
    bar_width = 0.35
    index = range(len(matchups))

    colors_home = ['green' if home_scores[i] > away_scores[i] else 'red' for i in range(len(home_scores))]
    colors_away = ['green' if away_scores[i] > home_scores[i] else 'red' for i in range(len(away_scores))]

    bar1 = ax.bar(index, home_scores, bar_width, color=colors_home)
    bar2 = ax.bar([i + bar_width for i in index], away_scores, bar_width, color=colors_away)

    # Add total points scored at the top of each bar
    for i in range(len(home_scores)):
        ax.text(i, home_scores[i] + 1, str(home_scores[i]), ha='center', va='bottom', fontsize=8)
        ax.text(i + bar_width, away_scores[i] + 1, str(away_scores[i]), ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Matchups')
    ax.set_ylabel('Scores')
    ax.set_title(f'Total Points Scored by Each Team - Week {week}')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels([''] * len(matchups))  # Remove x-tick labels

    # Create custom legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='green', label='Winning Team'),
                       Patch(facecolor='red', label='Losing Team')]
    ax.legend(handles=legend_elements)

    plt.tight_layout()

    # Add text at the bottom to indicate matchups and winners
    for i, (home_team, away_team, winner) in enumerate(winners):
        ax.text(i + bar_width / 2, -8, f"{home_team} vs {away_team}\nWinner: {winner}", ha='center', va='top', fontsize=10)

    # Clear the existing canvas if it exists
    global canvas
    if canvas:
        canvas.get_tk_widget().pack_forget()
        canvas = None

    # Display the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Adjust the canvas to fill and expand

def on_submit():
    week = week_entry.get()
    plot_data(week)

# Create the main window
root = tk.Tk()
root.title("Fantasy Football Data Viewer")

# Create a frame for the input and button
frame = tk.Frame(root)
frame.pack(pady=10)

# Create a label and entry for the week input
week_label = tk.Label(frame, text="Enter Week (1-10):")
week_label.pack(side=tk.LEFT, padx=5)
week_entry = tk.Entry(frame, width=5)
week_entry.pack(side=tk.LEFT, padx=5)

# Create a button to submit the week input
submit_button = tk.Button(frame, text="Submit", command=on_submit)
submit_button.pack(side=tk.LEFT, padx=5)

# Initialize the canvas variable
canvas = None

# Run the main event loop
root.mainloop()