import os 
import openai
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key= OPENAI_API_KEY
api_key = os.environ.get('STATPAL_API_KEY')



# the default URL's for the API endpoint
url_soccer = 'https://statpal.io/api/v1/soccer/livescores' 
url_nhl = 'https://statpal.io/api/v1/nhl/livescores'
url_nba = 'https://statpal.io/api/v1/nba/livescores'
url_nfl = 'https://statpal.io/api/v1/nfl/livescores'
url_mlb = 'https://statpal.io/api/v1/mlb/livescores'
url_tennis = 'https://statpal.io/api/v1/tennis/livescores'

params={"access_key":  api_key}

def fetch_sport_data(sport):
    """Fetch data for a specific sport"""
    url_map = {
        "soccer": url_soccer,
        "nhl": url_nhl,
        "nba": url_nba,
        "nfl": url_nfl,
        "mlb": url_mlb,
        "tennis": url_tennis
    }

    if sport not in url_map:
        return None  # If sport is not recognized

    try:
        response = requests.get(url_map[sport], params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {sport} data: {e}")
        return None
    


def save_to_json(data, filename="filtered_sport_data.json"):
    """Save filtered data to a JSON file"""
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Filtered data has been saved to {filename}")
    except Exception as e:
        print(f"Error saving filtered data to JSON file: {e}")


def safe_get_nested(obj, *keys, default='N/A'):
    """Safely get nested dictionary values with fallback."""
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return default
    return obj if obj is not None else default

def safe_get_venue(match):
    """Safely extract venue information from match data."""
    venue = match.get('venue_name')
    if venue:
        return venue
    
    venue_obj = match.get('venue')
    if isinstance(venue_obj, dict):
        return venue_obj.get('name', 'N/A')
    elif isinstance(venue_obj, str):
        return venue_obj
    
    return 'N/A'

def safe_get_nested(obj, *keys, default='N/A'):
    """Safely get nested dictionary values with fallback."""
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return default
    return obj if obj is not None else default

def safe_get_venue(match):
    """Safely extract venue information from match data."""
    venue = match.get('venue_name')
    if venue:
        return venue
    
    venue_obj = match.get('venue')
    if isinstance(venue_obj, dict):
        return venue_obj.get('name', 'N/A')
    elif isinstance(venue_obj, str):
        return venue_obj
    
    return 'N/A'

def filter_important_data(data, sport):
    """Filter and return the most important data from the response for any sport."""
    important_data = []
    
    # Debug: Print the structure of incoming data
    print(f"\n=== DEBUGGING {sport.upper()} ===")
    print(f"Data type: {type(data)}")
    print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"  {key}: {type(value)} - {len(value) if isinstance(value, (list, dict)) else 'N/A'}")
    
    # Handle different API response structures
    matches_data = []
    
    # Try different possible data structures
    if 'livescore' in data:
        # Structure: data -> livescore -> league -> match
        for league in data['livescore'].get('league', []):
            league_name = league.get('name', 'N/A')
            country = league.get('country', 'N/A')
            for match in league.get('match', []):
                matches_data.append((match, league_name, country))
    
    elif 'livescores' in data:
        # Structure: data -> livescores -> tournament -> match (for tennis, NHL, NFL, etc.)
        tournaments = data['livescores'].get('tournament', [])
        
        # Handle both single tournament (dict) and multiple tournaments (list)
        if isinstance(tournaments, dict):
            tournaments = [tournaments]
        
        for tournament in tournaments:
            league_name = tournament.get('name', tournament.get('league', 'N/A'))
            country = tournament.get('country', 'N/A')
            matches = tournament.get('match', [])
            
            # Handle both single match (dict) and multiple matches (list)
            if isinstance(matches, dict):
                matches = [matches]
            
            for match in matches:
                matches_data.append((match, league_name, country))
    
    elif 'matches' in data:
        # Structure: data -> matches
        for match in data['matches']:
            matches_data.append((match, 'N/A', 'N/A'))
    
    elif 'games' in data:
        # Structure: data -> games
        for match in data['games']:
            matches_data.append((match, 'N/A', 'N/A'))
    
    elif 'events' in data:
        # Structure: data -> events
        for match in data['events']:
            matches_data.append((match, 'N/A', 'N/A'))
    
    elif isinstance(data, list):
        # Direct list of matches
        for match in data:
            matches_data.append((match, 'N/A', 'N/A'))
    
    else:
        # Check for other possible top-level keys
        possible_keys = ['data', 'results', 'response', 'fixtures', 'schedule']
        for key in possible_keys:
            if key in data:
                sub_data = data[key]
                if isinstance(sub_data, list):
                    for match in sub_data:
                        matches_data.append((match, 'N/A', 'N/A'))
                elif isinstance(sub_data, dict):
                    # Try to find matches within this sub-data
                    for sub_key in ['matches', 'games', 'events', 'fixtures']:
                        if sub_key in sub_data and isinstance(sub_data[sub_key], list):
                            for match in sub_data[sub_key]:
                                matches_data.append((match, 'N/A', 'N/A'))
                break
    
    print(f"Found {len(matches_data)} potential matches to process")
    if matches_data and len(matches_data) > 0:
        print(f"Sample match keys: {list(matches_data[0][0].keys()) if isinstance(matches_data[0][0], dict) else 'Not a dict'}")
    print("=" * 50)
    
    # Process each match based on sport type
    for match, league_name, country in matches_data:
        if not isinstance(match, dict):
            continue
            
        # Initialize match info with default values
        match_info = {
            'time': 'N/A',
            'home_team': 'N/A',
            'home_score': 'N/A',
            'away_team': 'N/A',
            'away_score': 'N/A',
            'status': 'N/A',
            'league_name': league_name,
            'country': country,
            'venue': 'N/A',
            'sport': sport,
            'date': 'N/A'
        }
        
        try:
            # Extract common fields
            match_info['time'] = match.get('time', match.get('match_time', match.get('game_time', match.get('start_time', 'N/A'))))
            match_info['status'] = match.get('status', match.get('match_status', match.get('game_status', match.get('state', 'N/A'))))
            match_info['venue'] = safe_get_venue(match)
            match_info['date'] = match.get('date', match.get('formatted_date', 'N/A'))
            
            if sport.lower() == "soccer":
                match_info.update({
                    'home_team': safe_get_nested(match, 'home', 'name', default=
                                safe_get_nested(match, 'home_team', 'name', default='N/A')),
                    'home_score': safe_get_nested(match, 'home', 'goals', default=
                                 safe_get_nested(match, 'home_team', 'goals', default='N/A')),
                    'away_team': safe_get_nested(match, 'away', 'name', default=
                                safe_get_nested(match, 'away_team', 'name', default='N/A')),
                    'away_score': safe_get_nested(match, 'away', 'goals', default=
                                 safe_get_nested(match, 'away_team', 'goals', default='N/A'))
                })
            
            elif sport.lower() == "tennis":
                # Tennis uses player array instead of home/away
                players = match.get('player', [])
                if len(players) >= 2:
                    player1 = players[0]
                    player2 = players[1]
                    
                    match_info.update({
                        'home_team': player1.get('name', 'N/A'),
                        'home_score': player1.get('totalscore', player1.get('sets', 'N/A')),
                        'away_team': player2.get('name', 'N/A'),
                        'away_score': player2.get('totalscore', player2.get('sets', 'N/A')),
                        'set_score': match.get('set_score', 'N/A'),
                        'surface': match.get('surface', 'N/A'),
                        'game_score': f"{player1.get('game_score', '')} - {player2.get('game_score', '')}" if player1.get('game_score') or player2.get('game_score') else 'N/A'
                    })
                else:
                    # Fallback to home/away structure if player array is not available
                    match_info.update({
                        'home_team': safe_get_nested(match, 'home', 'name', default=
                                    safe_get_nested(match, 'player1', 'name', default='N/A')),
                        'home_score': safe_get_nested(match, 'home', 'score', default=
                                     safe_get_nested(match, 'player1', 'sets', default='N/A')),
                        'away_team': safe_get_nested(match, 'away', 'name', default=
                                    safe_get_nested(match, 'player2', 'name', default='N/A')),
                        'away_score': safe_get_nested(match, 'away', 'score', default=
                                     safe_get_nested(match, 'player2', 'sets', default='N/A'))
                    })
            
            elif sport.lower() == "nba":
                match_info.update({
                    'home_team': safe_get_nested(match, 'home', 'name', default=
                                safe_get_nested(match, 'home_team', 'name', default=
                                safe_get_nested(match, 'teams', 'home', 'name', default='N/A'))),
                    'home_score': safe_get_nested(match, 'home', 'score', default=
                                 safe_get_nested(match, 'home', 'totalscore', default=
                                 safe_get_nested(match, 'home_team', 'score', default=
                                 safe_get_nested(match, 'scores', 'home', default='N/A')))),
                    'away_team': safe_get_nested(match, 'away', 'name', default=
                                safe_get_nested(match, 'away_team', 'name', default=
                                safe_get_nested(match, 'teams', 'away', 'name', default='N/A'))),
                    'away_score': safe_get_nested(match, 'away', 'score', default=
                                 safe_get_nested(match, 'away', 'totalscore', default=
                                 safe_get_nested(match, 'away_team', 'score', default=
                                 safe_get_nested(match, 'scores', 'away', default='N/A')))),
                    'quarter': match.get('period', match.get('quarter', 'N/A')),
                    'time_remaining': match.get('time_remaining', 'N/A')
                })
            
            elif sport.lower() == "nfl":
                match_info.update({
                    'home_team': safe_get_nested(match, 'home', 'name', default=
                                safe_get_nested(match, 'home_team', 'name', default=
                                safe_get_nested(match, 'teams', 'home', 'name', default='N/A'))),
                    'home_score': safe_get_nested(match, 'home', 'totalscore', default=
                                 safe_get_nested(match, 'home', 'score', default=
                                 safe_get_nested(match, 'home_team', 'score', default=
                                 safe_get_nested(match, 'scores', 'home', default='N/A')))),
                    'away_team': safe_get_nested(match, 'away', 'name', default=
                                safe_get_nested(match, 'away_team', 'name', default=
                                safe_get_nested(match, 'teams', 'away', 'name', default='N/A'))),
                    'away_score': safe_get_nested(match, 'away', 'totalscore', default=
                                 safe_get_nested(match, 'away', 'score', default=
                                 safe_get_nested(match, 'away_team', 'score', default=
                                 safe_get_nested(match, 'scores', 'away', default='N/A')))),
                    'quarter': match.get('period', match.get('quarter', 'N/A')),
                    'week': match.get('week', 'N/A'),
                    'time_remaining': match.get('timer', match.get('time_remaining', 'N/A')),
                    'attendance': match.get('attendance', 'N/A'),
                    'venue_name': match.get('venue_name', 'N/A'),
                    'quarter_scores': {
                        'q1': f"{safe_get_nested(match, 'home', 'q1', default='0')}-{safe_get_nested(match, 'away', 'q1', default='0')}",
                        'q2': f"{safe_get_nested(match, 'home', 'q2', default='0')}-{safe_get_nested(match, 'away', 'q2', default='0')}",
                        'q3': f"{safe_get_nested(match, 'home', 'q3', default='0')}-{safe_get_nested(match, 'away', 'q3', default='0')}",
                        'q4': f"{safe_get_nested(match, 'home', 'q4', default='0')}-{safe_get_nested(match, 'away', 'q4', default='0')}"
                    }
                })
            
            elif sport.lower() == "mlb":
                match_info.update({
                    'home_team': safe_get_nested(match, 'home', 'name', default=
                                safe_get_nested(match, 'home', 'team_name', default=
                                safe_get_nested(match, 'home_team', 'name', default=
                                safe_get_nested(match, 'teams', 'home', 'name', default='N/A')))),
                    'home_score': safe_get_nested(match, 'home', 'totalscore', default=
                                 safe_get_nested(match, 'home', 'score', default=
                                 safe_get_nested(match, 'home', 'runs', default=
                                 safe_get_nested(match, 'home_team', 'runs', default=
                                 safe_get_nested(match, 'scores', 'home', default='N/A'))))),
                    'away_team': safe_get_nested(match, 'away', 'name', default=
                                safe_get_nested(match, 'away', 'team_name', default=
                                safe_get_nested(match, 'away_team', 'name', default=
                                safe_get_nested(match, 'teams', 'away', 'name', default='N/A')))),
                    'away_score': safe_get_nested(match, 'away', 'totalscore', default=
                                 safe_get_nested(match, 'away', 'score', default=
                                 safe_get_nested(match, 'away', 'runs', default=
                                 safe_get_nested(match, 'away_team', 'runs', default=
                                 safe_get_nested(match, 'scores', 'away', default='N/A'))))),
                    'inning': match.get('inning', match.get('current_inning', 'N/A')),
                    'outs': match.get('outs', 'N/A')
                })
            
            elif sport.lower() == "nhl":
                match_info.update({
                    'home_team': safe_get_nested(match, 'home', 'name', default=
                                safe_get_nested(match, 'home_team', 'name', default=
                                safe_get_nested(match, 'teams', 'home', 'name', default='N/A'))),
                    'home_score': safe_get_nested(match, 'home', 'totalscore', default=
                                 safe_get_nested(match, 'home', 'score', default=
                                 safe_get_nested(match, 'home_team', 'score', default=
                                 safe_get_nested(match, 'scores', 'home', default='N/A')))),
                    'away_team': safe_get_nested(match, 'away', 'name', default=
                                safe_get_nested(match, 'away_team', 'name', default=
                                safe_get_nested(match, 'teams', 'away', 'name', default='N/A'))),
                    'away_score': safe_get_nested(match, 'away', 'totalscore', default=
                                 safe_get_nested(match, 'away', 'score', default=
                                 safe_get_nested(match, 'away_team', 'score', default=
                                 safe_get_nested(match, 'scores', 'away', default='N/A')))),
                    'period': match.get('period', 'N/A'),
                    'time_remaining': match.get('timer', match.get('time_remaining', 'N/A')),
                    'fix_id': match.get('fix_id', 'N/A')
                })
            
            # Only add matches with valid team names
            if match_info['home_team'] != 'N/A' and match_info['away_team'] != 'N/A':
                important_data.append(match_info)
                
        except Exception as e:
            print(f"Error processing match data for {sport}: {e}")
            print(f"Match data: {match}")
            continue
    
    print(f"Successfully processed {len(important_data)} matches for {sport}")
    return important_data



# Test the function
if __name__ == "__main__":
    sport = "soccer"  # Example: You can change it to any sport like 'nba', 'nfl', etc.
    data = fetch_sport_data(sport)
    if data:
        # Pass the sport as a second argument to filter_important_data
        filtered_data = filter_important_data(data, sport)  # Make sure sport is passed here
        
        # Print the filtered data for inspection
        print(f"Filtered data for {sport}:")
        print(json.dumps(filtered_data, indent=4))

        # Save the filtered data to a JSON file
        save_to_json(filtered_data, filename=f"{sport}_filtered_data.json")
    else:
        print(f"Could not fetch data for {sport}")