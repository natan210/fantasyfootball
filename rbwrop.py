import requests
import matplotlib.pyplot as plt

year = 2024
league_id = "1821897649"
swid = "{9A7CC82B-E2EF-4BC6-A945-03355F0551BA}"
espn_s2 = "AECy9hVogBZqVHEf%2FRRb8EN%2BbsHrkLEBB1o4mrzFE67BmNOF6F%2B9WyRDv6IejeljCXULm6wATwskH3F7qs0LssX8ZYhwlZG7gt%2FuKkv%2ByTv4EkMgErZOHDo02j0QdhvDat6rtR0ITQ3utT%2FsSq4NHXLpquCP1ZuM9hcnurtcp%2F%2FIy5LqLiyoEOl9yU%2FJLfHKDpWVnhYOFHd4xOmMLgxu3si7D8rJMnyrB92kIYz1XhXo8rdci7unqx6O1lgB3UvL4F%2BxjaakdWp15kr9rMvW3n2znai%2FQ6ZKdSjujUTlUss3uZ4I6L1nHu2%2BM3sgpm2a2rDMtFhu8fIvK%2Bg8jnFsnlKw"

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
    'Referer': 'https://fantasy.espn.com/',
    'Origin': 'https://fantasy.espn.com',
    'x-fantasy-platform': 'kona-PROD-c495d34b311913252eb42e5284fe45c2a8cfbdc5',
    'x-fantasy-source': 'kona'
}

cookies = {
    "SWID": swid,
    "espn_s2": espn_s2
}

# Global dictionary to store the total stat total for each team
team_stat_totals = {}

#qb's are 1, rb's are 2, wr's are 3, te's are 4, k's are 5, dst are 16, using defaultPositionId
def get_optimal_pf(team, team_id):
    if 'rosterForCurrentScoringPeriod' not in team:
        return
    
    optimal_points = calculate_optimal_points(team)
    sorted_optimal_points = sort_optimal_points(optimal_points)
    optimal_lineup = initialize_optimal_lineup()
    position_counts = initialize_position_counts()
    fill_optimal_lineup(sorted_optimal_points, optimal_lineup, position_counts)
    
    # Calculate the total appliedStatTotal for the optimal lineup
    total_stat_total = 0
    for position, player in optimal_lineup.items():
        if isinstance(player, list):
            for p in player:
                total_stat_total += p[1]['appliedStatTotal']
        else:
            total_stat_total += player[1]['appliedStatTotal']
    
    # Add the total stat total for the team to the global dictionary
    if team_id in team_stat_totals:
        team_stat_totals[team_id] += total_stat_total
    else:
        team_stat_totals[team_id] = total_stat_total
    
    return optimal_lineup

def calculate_optimal_points(team):
    optimal_points = {}
    for player in team['rosterForCurrentScoringPeriod']['entries']:
        player_name = player['playerPoolEntry']['player']['fullName']
        player_position_id = player['playerPoolEntry']['player']['defaultPositionId']
        player_points = player['playerPoolEntry']['appliedStatTotal']
        if player_name in optimal_points:
            optimal_points[player_name]['appliedStatTotal'] += player_points
        else:
            optimal_points[player_name] = {
                'defaultPositionId': player_position_id,
                'appliedStatTotal': player_points
            }
    return optimal_points

def sort_optimal_points(optimal_points):
    return sorted(optimal_points.items(), key=lambda item: item[1]['appliedStatTotal'], reverse=True)

def initialize_optimal_lineup():
    return {
        1: None,  # QB
        2: [],    # RB
        3: [],    # WR
        4: None,  # TE
        5: None,  # K
        16: None, # DST
        'flex': None  # Flex (RB, WR, or TE)
    }

def initialize_position_counts():
    return {1: 1, 2: 2, 3: 2, 4: 1, 5: 1, 16: 1}

def fill_optimal_lineup(sorted_optimal_points, optimal_lineup, position_counts):
    for player_name, stats in sorted_optimal_points:
        position_id = stats['defaultPositionId']
        if position_id in position_counts and position_counts[position_id] > 0:
            if position_id == 1:
                optimal_lineup[1] = (player_name, stats)
            elif position_id == 2:
                optimal_lineup[2].append((player_name, stats))
            elif position_id == 3:
                optimal_lineup[3].append((player_name, stats))
            elif position_id == 4:
                optimal_lineup[4] = (player_name, stats)
            elif position_id == 5:
                optimal_lineup[5] = (player_name, stats)
            elif position_id == 16:
                optimal_lineup[16] = (player_name, stats)
            position_counts[position_id] -= 1
        elif position_id in [2, 3, 4] and optimal_lineup['flex'] is None:
            optimal_lineup['flex'] = (player_name, stats)

# Main code to process the data for weeks 1 and 2
try:
    for week in range(16, 18):
        url = 'https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{}/segments/0/leagues/{}?scoringPeriodId={}&view=mBoxscore&view=mMatchupScore&view=mRoster&view=mSettings&view=mStatus&view=mTeam&view=modular&view=mNav'.format(year, league_id, week)
        r = requests.get(url, headers=headers, cookies=cookies)
        r.raise_for_status()  # Check for HTTP errors
        data = r.json()
        
        team_map = {team['id']: team for team in data['teams']}
        matchups = []
        home_scores = []
        away_scores = []
        winners = []
        optimalPF = {} # 8 elements, 1 for each team. 

        # Extract and print the total points scored by each team
        for matchup in data['schedule']:
            home_team_id = matchup['home']['teamId']
            home_score = matchup['home']['totalPoints']
            away_team_id = matchup['away']['teamId']
            away_score = matchup['away']['totalPoints']

            get_optimal_pf(matchup['away'], away_team_id)
            get_optimal_pf(matchup['home'], home_team_id)

            home_team_name = team_map[home_team_id]['name']
            away_team_name = team_map[away_team_id]['name']

            matchups.append(f"{home_team_name} vs {away_team_name}")
            home_scores.append(home_score)
            away_scores.append(away_score)

    # Sort the total stat totals by highest to lowest
    sorted_team_stat_totals = sorted(team_stat_totals.items(), key=lambda item: item[1], reverse=True)

    # Print the total stat totals for each team
    for team_id, total in sorted_team_stat_totals:
        team_name = team_map[team_id]['name']
        print(f"Team {team_name}: Total Stat Total = {total:.2f}")

except requests.exceptions.RequestException as e:
    print(f"HTTP Request failed: {e}")
except ValueError as e:
    print(f"Error parsing JSON: {e}")
    print(f"Response content: {r.content}")