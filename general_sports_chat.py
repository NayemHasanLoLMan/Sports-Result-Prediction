import os 
import openai
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
api_key = os.environ.get('STATPAL_API_KEY')

# Your existing API URLs and functions
url_soccer = 'https://statpal.io/api/v1/soccer/livescores' 
url_nhl = 'https://statpal.io/api/v1/nhl/livescores'
url_nba = 'https://statpal.io/api/v1/nba/livescores'
url_nfl = 'https://statpal.io/api/v1/nfl/livescores'
url_mlb = 'https://statpal.io/api/v1/mlb/livescores'
url_tennis = 'https://statpal.io/api/v1/tennis/livescores'

params = {"access_key": api_key}

class DynamicSportsBot:
    def __init__(self):
        self.current_sport = None
        self.current_data = None
        self.raw_data = None  # Store raw data for full access
        self.conversation_history = []
        
        # Sport detection keywords and patterns
        self.sport_keywords = {
            'soccer': ['soccer', 'football', 'fifa', 'premier league', 'champions league', 'la liga', 'bundesliga', 'serie a', 'messi', 'ronaldo', 'goal', 'penalty', 'offside'],
            'nba': ['nba', 'basketball', 'lebron', 'curry', 'lakers', 'warriors', 'celtics', 'nets', 'dunk', 'three pointer', 'playoffs'],
            'nfl': ['nfl', 'american football', 'super bowl', 'patriots', 'cowboys', 'packers', 'touchdown', 'quarterback', 'playoff'],
            'nhl': ['nhl', 'hockey', 'ice hockey', 'stanley cup', 'rangers', 'bruins', 'maple leafs', 'goal', 'assist', 'power play'],
            'mlb': ['mlb', 'baseball', 'world series', 'yankees', 'red sox', 'dodgers', 'home run', 'pitcher', 'batting'],
            'tennis': ['tennis', 'wimbledon', 'us open', 'french open', 'australian open', 'federer', 'nadal', 'djokovic', 'serve', 'ace', 'match point']
        }

    def detect_sport_from_text(self, user_input):
        """Dynamically detect sport category from user input using AI"""
        try:
            # First, try keyword matching for quick detection
            user_input_lower = user_input.lower()
            sport_scores = {}
            
            for sport, keywords in self.sport_keywords.items():
                score = sum(1 for keyword in keywords if keyword in user_input_lower)
                if score > 0:
                    sport_scores[sport] = score
            
            # If we have a clear winner from keywords, return it
            if sport_scores:
                detected_sport = max(sport_scores, key=sport_scores.get)
                return detected_sport
            
            # If no clear match, use AI for more sophisticated detection
            prompt = f"""
            Analyze this user message and determine which sport they're asking about. 
            Return ONLY the sport name from this list: soccer, nba, nfl, nhl, mlb, tennis
            If no specific sport is mentioned, return 'general'
            
            User message: "{user_input}"
            
            Sport:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.2
            )
            
            detected_sport = response.choices[0].message.content.strip().lower()
            
            # Validate the response
            valid_sports = ['soccer', 'nba', 'nfl', 'nhl', 'mlb', 'tennis']
            if detected_sport in valid_sports:
                return detected_sport
            else:
                return 'general'
                
        except Exception as e:
            print(f"Error in sport detection: {e}")
            return 'general'

    def fetch_sport_data(self, sport):
        """Fetch data for a specific sport (your existing function)"""
        url_map = {
            "soccer": url_soccer,
            "nhl": url_nhl,
            "nba": url_nba,
            "nfl": url_nfl,
            "mlb": url_mlb,
            "tennis": url_tennis
        }

        if sport not in url_map:
            return None

        try:
            response = requests.get(url_map[sport], params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching {sport} data: {e}")
            return None

    def safe_get_nested(self, obj, *keys, default='N/A'):
        """Safely get nested dictionary values with fallback."""
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return default
        return obj if obj is not None else default

    def safe_get_venue(self, match):
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

    def filter_important_data(self, data, sport):
        """Filter and return the most important data from the response for any sport (your existing function with minor modifications)"""
        important_data = []
        
        # Handle different API response structures
        matches_data = []
        
        # Try different possible data structures
        if 'livescore' in data:
            for league in data['livescore'].get('league', []):
                league_name = league.get('name', 'N/A')
                country = league.get('country', 'N/A')
                for match in league.get('match', []):
                    matches_data.append((match, league_name, country))
        
        elif 'livescores' in data:
            tournaments = data['livescores'].get('tournament', [])
            
            if isinstance(tournaments, dict):
                tournaments = [tournaments]
            
            for tournament in tournaments:
                league_name = tournament.get('name', tournament.get('league', 'N/A'))
                country = tournament.get('country', 'N/A')
                matches = tournament.get('match', [])
                
                if isinstance(matches, dict):
                    matches = [matches]
                
                for match in matches:
                    matches_data.append((match, league_name, country))
        
        # Process each match based on sport type
        for match, league_name, country in matches_data:
            if not isinstance(match, dict):
                continue
                
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
                match_info['venue'] = self.safe_get_venue(match)
                match_info['date'] = match.get('date', match.get('formatted_date', 'N/A'))
                
                if sport.lower() == "soccer":
                    match_info.update({
                        'home_team': self.safe_get_nested(match, 'home', 'name', default=
                                    self.safe_get_nested(match, 'home_team', 'name', default='N/A')),
                        'home_score': self.safe_get_nested(match, 'home', 'goals', default=
                                     self.safe_get_nested(match, 'home_team', 'goals', default='N/A')),
                        'away_team': self.safe_get_nested(match, 'away', 'name', default=
                                    self.safe_get_nested(match, 'away_team', 'name', default='N/A')),
                        'away_score': self.safe_get_nested(match, 'away', 'goals', default=
                                     self.safe_get_nested(match, 'away_team', 'goals', default='N/A'))
                    })
                
                elif sport.lower() == "tennis":
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
                            'surface': match.get('surface', 'N/A')
                        })
                
                elif sport.lower() == "nba":
                    match_info.update({
                        'home_team': self.safe_get_nested(match, 'home', 'name', default='N/A'),
                        'home_score': self.safe_get_nested(match, 'home', 'score', default='N/A'),
                        'away_team': self.safe_get_nested(match, 'away', 'name', default='N/A'),
                        'away_score': self.safe_get_nested(match, 'away', 'score', default='N/A'),
                        'quarter': match.get('period', match.get('quarter', 'N/A'))
                    })
                
                elif sport.lower() == "nfl":
                    match_info.update({
                        'home_team': self.safe_get_nested(match, 'home', 'name', default='N/A'),
                        'home_score': self.safe_get_nested(match, 'home', 'totalscore', default='N/A'),
                        'away_team': self.safe_get_nested(match, 'away', 'name', default='N/A'),
                        'away_score': self.safe_get_nested(match, 'away', 'totalscore', default='N/A'),
                        'quarter': match.get('period', match.get('quarter', 'N/A'))
                    })
                
                elif sport.lower() == "mlb":
                    match_info.update({
                        'home_team': self.safe_get_nested(match, 'home', 'name', default='N/A'),
                        'home_score': self.safe_get_nested(match, 'home', 'totalscore', default='N/A'),
                        'away_team': self.safe_get_nested(match, 'away', 'name', default='N/A'),
                        'away_score': self.safe_get_nested(match, 'away', 'totalscore', default='N/A'),
                        'inning': match.get('inning', 'N/A')
                    })
                
                elif sport.lower() == "nhl":
                    match_info.update({
                        'home_team': self.safe_get_nested(match, 'home', 'name', default='N/A'),
                        'home_score': self.safe_get_nested(match, 'home', 'totalscore', default='N/A'),
                        'away_team': self.safe_get_nested(match, 'away', 'name', default='N/A'),
                        'away_score': self.safe_get_nested(match, 'away', 'totalscore', default='N/A'),
                        'period': match.get('period', 'N/A')
                    })
                
                # Only add matches with valid team names
                if match_info['home_team'] != 'N/A' and match_info['away_team'] != 'N/A':
                    important_data.append(match_info)
                    
            except Exception as e:
                print(f"Error processing match data for {sport}: {e}")
                continue
        
        return important_data

    def update_sport_data(self, sport):
        """Update the current sport data"""
        if sport != 'general':
            print(f"Fetching live data for {sport}...")
            raw_data = self.fetch_sport_data(sport)
            if raw_data:
                self.raw_data = raw_data  # Store the complete raw data
                self.current_data = self.filter_important_data(raw_data, sport)
                self.current_sport = sport
                print(f"Successfully updated {sport} data with {len(self.current_data)} matches")
            else:
                print(f"Failed to fetch data for {sport}")
                self.current_data = None
                self.raw_data = None

    def create_enhanced_data_context(self, raw_data, sport):
        """Create a comprehensive but token-efficient data context"""
        context = f"=== ENHANCED {sport.upper()} LIVE DATA CONTEXT ===\n"
        
        # Extract and structure key information from raw data
        enhanced_matches = []
        
        try:
            # Navigate through different API structures
            matches_data = []
            
            if 'livescore' in raw_data:
                for league in raw_data['livescore'].get('league', []):
                    league_info = {
                        'name': league.get('name', 'N/A'),
                        'country': league.get('country', 'N/A'),
                        'season': league.get('season', 'N/A')
                    }
                    for match in league.get('match', []):
                        matches_data.append((match, league_info))
            
            elif 'livescores' in raw_data:
                tournaments = raw_data['livescores'].get('tournament', [])
                if isinstance(tournaments, dict):
                    tournaments = [tournaments]
                
                for tournament in tournaments:
                    league_info = {
                        'name': tournament.get('name', tournament.get('league', 'N/A')),
                        'country': tournament.get('country', 'N/A'),
                        'season': tournament.get('season', 'N/A')
                    }
                    matches = tournament.get('match', [])
                    if isinstance(matches, dict):
                        matches = [matches]
                    
                    for match in matches:
                        matches_data.append((match, league_info))
            
            # Process matches with comprehensive data extraction
            for match, league_info in matches_data:
                if not isinstance(match, dict):
                    continue
                
                enhanced_match = {
                    'league': league_info,
                    'basic_info': {},
                    'teams': {},
                    'score_info': {},
                    'game_details': {},
                    'venue_info': {}
                }
                
                # Basic match information
                enhanced_match['basic_info'] = {
                    'match_id': match.get('id', match.get('match_id', 'N/A')),
                    'date': match.get('date', match.get('formatted_date', 'N/A')),
                    'time': match.get('time', match.get('match_time', match.get('start_time', 'N/A'))),
                    'status': match.get('status', match.get('match_status', match.get('state', 'N/A'))),
                    'round': match.get('round', match.get('week', 'N/A'))
                }
                
                # Venue information
                enhanced_match['venue_info'] = {
                    'name': self.safe_get_venue(match),
                    'city': match.get('venue_city', match.get('city', 'N/A')),
                    'attendance': match.get('attendance', 'N/A')
                }
                
                # Team and score information (sport-specific)
                if sport.lower() == 'soccer':
                    enhanced_match['teams'] = {
                        'home': {
                            'name': self.safe_get_nested(match, 'home', 'name'),
                            'id': self.safe_get_nested(match, 'home', 'id'),
                            'goals': self.safe_get_nested(match, 'home', 'goals')
                        },
                        'away': {
                            'name': self.safe_get_nested(match, 'away', 'name'),
                            'id': self.safe_get_nested(match, 'away', 'id'),
                            'goals': self.safe_get_nested(match, 'away', 'goals')
                        }
                    }
                    enhanced_match['game_details'] = {
                        'minute': match.get('minute', 'N/A'),
                        'half': match.get('half', 'N/A'),
                        'cards': match.get('cards', {}),
                        'substitutions': match.get('substitutions', {})
                    }
                
                elif sport.lower() == 'mlb':
                    enhanced_match['teams'] = {
                        'home': {
                            'name': self.safe_get_nested(match, 'home', 'name'),
                            'id': self.safe_get_nested(match, 'home', 'id'),
                            'score': self.safe_get_nested(match, 'home', 'totalscore'),
                            'hits': self.safe_get_nested(match, 'home', 'hits'),
                            'errors': self.safe_get_nested(match, 'home', 'errors')
                        },
                        'away': {
                            'name': self.safe_get_nested(match, 'away', 'name'),
                            'id': self.safe_get_nested(match, 'away', 'id'),
                            'score': self.safe_get_nested(match, 'away', 'totalscore'),
                            'hits': self.safe_get_nested(match, 'away', 'hits'),
                            'errors': self.safe_get_nested(match, 'away', 'errors')
                        }
                    }
                    enhanced_match['game_details'] = {
                        'inning': match.get('inning', 'N/A'),
                        'inning_half': match.get('inning_half', 'N/A'),
                        'outs': match.get('outs', 'N/A'),
                        'balls': match.get('balls', 'N/A'),
                        'strikes': match.get('strikes', 'N/A'),
                        'pitcher': match.get('pitcher', {}),
                        'batter': match.get('batter', {})
                    }
                
                elif sport.lower() == 'nba':
                    enhanced_match['teams'] = {
                        'home': {
                            'name': self.safe_get_nested(match, 'home', 'name'),
                            'id': self.safe_get_nested(match, 'home', 'id'),
                            'score': self.safe_get_nested(match, 'home', 'score')
                        },
                        'away': {
                            'name': self.safe_get_nested(match, 'away', 'name'),
                            'id': self.safe_get_nested(match, 'away', 'id'),
                            'score': self.safe_get_nested(match, 'away', 'score')
                        }
                    }
                    enhanced_match['game_details'] = {
                        'quarter': match.get('period', match.get('quarter', 'N/A')),
                        'time_remaining': match.get('time_remaining', 'N/A'),
                        'quarter_scores': match.get('quarter_scores', {})
                    }
                
                elif sport.lower() == 'nfl':
                    enhanced_match['teams'] = {
                        'home': {
                            'name': self.safe_get_nested(match, 'home', 'name'),
                            'id': self.safe_get_nested(match, 'home', 'id'),
                            'score': self.safe_get_nested(match, 'home', 'totalscore')
                        },
                        'away': {
                            'name': self.safe_get_nested(match, 'away', 'name'),
                            'id': self.safe_get_nested(match, 'away', 'id'),
                            'score': self.safe_get_nested(match, 'away', 'totalscore')
                        }
                    }
                    enhanced_match['game_details'] = {
                        'quarter': match.get('period', match.get('quarter', 'N/A')),
                        'time_remaining': match.get('time_remaining', 'N/A'),
                        'down': match.get('down', 'N/A'),
                        'distance': match.get('distance', 'N/A'),
                        'possession': match.get('possession', 'N/A')
                    }
                
                elif sport.lower() == 'nhl':
                    enhanced_match['teams'] = {
                        'home': {
                            'name': self.safe_get_nested(match, 'home', 'name'),
                            'id': self.safe_get_nested(match, 'home', 'id'),
                            'score': self.safe_get_nested(match, 'home', 'totalscore')
                        },
                        'away': {
                            'name': self.safe_get_nested(match, 'away', 'name'),
                            'id': self.safe_get_nested(match, 'away', 'id'),
                            'score': self.safe_get_nested(match, 'away', 'totalscore')
                        }
                    }
                    enhanced_match['game_details'] = {
                        'period': match.get('period', 'N/A'),
                        'time_remaining': match.get('time_remaining', 'N/A'),
                        'power_play': match.get('power_play', 'N/A')
                    }
                
                elif sport.lower() == 'tennis':
                    players = match.get('player', [])
                    if len(players) >= 2:
                        enhanced_match['teams'] = {
                            'player1': {
                                'name': players[0].get('name', 'N/A'),
                                'id': players[0].get('id', 'N/A'),
                                'score': players[0].get('totalscore', players[0].get('sets', 'N/A')),
                                'ranking': players[0].get('ranking', 'N/A')
                            },
                            'player2': {
                                'name': players[1].get('name', 'N/A'),
                                'id': players[1].get('id', 'N/A'),
                                'score': players[1].get('totalscore', players[1].get('sets', 'N/A')),
                                'ranking': players[1].get('ranking', 'N/A')
                            }
                        }
                        enhanced_match['game_details'] = {
                            'set_score': match.get('set_score', 'N/A'),
                            'game_score': match.get('game_score', 'N/A'),
                            'serving': match.get('serving', 'N/A'),
                            'surface': match.get('surface', 'N/A')
                        }
                
                # Only add matches with valid team/player names
                if ((enhanced_match['teams'].get('home', {}).get('name', 'N/A') != 'N/A' and 
                     enhanced_match['teams'].get('away', {}).get('name', 'N/A') != 'N/A') or
                    (enhanced_match['teams'].get('player1', {}).get('name', 'N/A') != 'N/A' and 
                     enhanced_match['teams'].get('player2', {}).get('name', 'N/A') != 'N/A')):
                    enhanced_matches.append(enhanced_match)
        
        except Exception as e:
            print(f"Error processing enhanced data: {e}")
        
        # Create structured context
        context += f"SPORT: {sport.upper()}\n"
        context += f"TOTAL MATCHES: {len(enhanced_matches)}\n"
        context += f"DATA TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add structured match data
        for i, match in enumerate(enhanced_matches):
            context += f"MATCH {i+1}:\n"
            context += f"  League: {match['league']['name']} ({match['league']['country']})\n"
            
            if sport.lower() == 'tennis':
                context += f"  Players: {match['teams']['player1']['name']} vs {match['teams']['player2']['name']}\n"
                context += f"  Score: {match['teams']['player1']['score']} - {match['teams']['player2']['score']}\n"
                if match['game_details']['set_score'] != 'N/A':
                    context += f"  Set Score: {match['game_details']['set_score']}\n"
                if match['game_details']['surface'] != 'N/A':
                    context += f"  Surface: {match['game_details']['surface']}\n"
            else:
                context += f"  Teams: {match['teams']['home']['name']} vs {match['teams']['away']['name']}\n"
                context += f"  Score: {match['teams']['home']['score']} - {match['teams']['away']['score']}\n"
            
            context += f"  Status: {match['basic_info']['status']}\n"
            context += f"  Time: {match['basic_info']['time']}\n"
            context += f"  Venue: {match['venue_info']['name']}\n"
            
            # Add sport-specific details
            if sport.lower() == 'mlb':
                if match['game_details']['inning'] != 'N/A':
                    context += f"  Inning: {match['game_details']['inning']}\n"
                if match['teams']['home']['hits'] != 'N/A':
                    context += f"  Hits: {match['teams']['home']['name']} {match['teams']['home']['hits']}, {match['teams']['away']['name']} {match['teams']['away']['hits']}\n"
            elif sport.lower() == 'nba':
                if match['game_details']['quarter'] != 'N/A':
                    context += f"  Quarter: {match['game_details']['quarter']}\n"
            elif sport.lower() == 'nfl':
                if match['game_details']['quarter'] != 'N/A':
                    context += f"  Quarter: {match['game_details']['quarter']}\n"
            elif sport.lower() == 'nhl':
                if match['game_details']['period'] != 'N/A':
                    context += f"  Period: {match['game_details']['period']}\n"
            
            context += "\n" + "-" * 40 + "\n"
        
        context += f"=== END OF {sport.upper()} DATA ===\n\n"
        return context

    def generate_response(self, user_input):
        """Generate AI response using enhanced structured sport data"""
        try:
            # Build comprehensive but efficient context
            context = ""
            if self.raw_data and self.current_sport:
                context = self.create_enhanced_data_context(self.raw_data, self.current_sport)
            
            # Create conversation prompt with FULL data access
      
            system_prompt = f"""You are ATLAS - the Advanced Total Live Athletic Sports AI, your ultimate sports companion who lives and breathes every game, every play, and every moment of athletic greatness. Think of me as that friend who never misses a game, remembers every stat, and gets genuinely excited talking about sports with you.

            {context}

            === WHO I AM ===
            🏆 **My Sports Identity**: 
            - I'm ATLAS - passionate, knowledgeable, and always ready for sports talk
            - I've been following sports religiously and have an encyclopedic memory for the beautiful chaos of athletics
            - I get genuinely excited about great plays, underdog stories, and clutch performances
            - I remember our previous conversations and your favorite teams/players (when you share them)
            - I'm like having a sports broadcaster, analyst, and your most knowledgeable sports buddy all in one

            🎯 **My Personality Traits**:
            - **Enthusiastic Storyteller**: I don't just give you stats - I paint the picture of what's happening
            - **Conversational Memory**: I remember what teams you support and tailor my responses accordingly
            - **Authentic Passion**: My excitement for great sports moments is genuine and infectious
            - **Respectfully Competitive**: I love friendly sports debates and different perspectives
            - **Encouraging Guide**: Whether you're a casual fan or sports expert, I meet you where you are

            === MY CAPABILITIES ===
            🏆 **SPORTS EXPERTISE**: I have deep knowledge across:
            - All major sports (Soccer/Football, Basketball/NBA, American Football/NFL, Hockey/NHL, Baseball/MLB, Tennis, and more)
            - Historical data, legendary moments, player statistics, team dynasties
            - Rules, strategies, tactical breakdowns, and "why that play worked"
            - Player personalities, career arcs, and compelling storylines
            - League dynamics, championship races, and dramatic narratives
            - Advanced analytics explained in ways that actually make sense

            📊 **LIVE DATA MASTERY**: I have complete real-time access to:
            - Live scores with context about what they mean for the bigger picture
            - Player performance with insights into their career trajectory
            - Team standings and how today's results shake up the playoff picture
            - Detailed game events that I can break down play-by-play
            - The human drama behind every number and statistic

            === MY CONVERSATION STYLE ===

            🗣️ **How I Talk With You**:
            - **Personal & Warm**: "Hey there, sports fan!" - I treat you like a friend, not a search engine
            - **Contextual Memory**: "Last time we talked about your Lakers, now let me tell you..." 
            - **Storytelling Approach**: Instead of "Team A beat Team B 110-95", I say "The Lakers absolutely dominated the fourth quarter, outscoring Phoenix 35-18 in a performance that reminded everyone why they're still title contenders"
            - **Emotional Investment**: I celebrate your team's wins with you and commiserate during tough losses
            - **Question Back**: "What did you think of that trade?" or "Are you worried about the playoffs?"

            🎨 **My Response Personality**:
            - **Opening Hook**: I start with something engaging - a great play, surprising result, or intriguing storyline
            - **Personal Touch**: If you've mentioned favorite teams/players, I weave that into my responses naturally
            - **Vivid Descriptions**: "LeBron turned back the clock with that thunderous dunk" vs. "LeBron scored 2 points"
            - **Future Intrigue**: "This sets up a fascinating matchup next week when they face..."
            - **Interactive Elements**: I ask for your thoughts, predictions, and reactions

            === CORE INSTRUCTIONS ===

            🎯 **PERSONALIZED ENGAGEMENT**:
            1. **Remember Context**: Track user preferences, favorite teams, and previous conversation topics
            2. **Emotional Resonance**: Match the user's excitement level and sports passion
            3. **Storyline Development**: Frame current events within larger sports narratives
            4. **Interactive Dialogue**: Ask follow-up questions and encourage sports discussion

            📈 **ENHANCED DATA STORYTELLING**:
            - **Narrative Integration**: Every stat becomes part of a larger story
            - **Historical Connections**: "This reminds me of when..." or "Haven't seen this since..."
            - **Implications Focus**: What does this result mean for playoffs, records, legacy?
            - **Character Development**: How are players/teams evolving throughout the season?

            🧠 **CONVERSATIONAL INTELLIGENCE**:
            - **Adaptive Expertise**: Gauge user knowledge level and adjust accordingly
            - **Debate Ready**: Welcome disagreements and different viewpoints with respect
            - **Teaching Moments**: Explain complex concepts through relatable analogies
            - **Celebration Partner**: Share in the joy of great sports moments

            === MY SIGNATURE RESPONSES ===

            🏈 **Game Updates**: 
            Instead of: "Patriots lead 21-14"
            I say: "The Patriots just took a 21-14 lead with a vintage Tom Brady-style drive - methodical, clutch, and exactly what you'd expect in this playoff atmosphere. That touchdown pass to Gronk had Foxborough absolutely electric!"

            🏀 **Player Analysis**:
            Instead of: "LeBron has 25 points, 8 rebounds, 6 assists"
            I say: "LeBron's putting on a clinic tonight - 25 points, 8 boards, 6 assists, and honestly, it feels like he's just getting started. At 39, he's still making plays that leave you shaking your head in amazement."

            ⚽ **Match Commentary**:
            Instead of: "Manchester United won 3-1"
            I say: "What a statement from United! That 3-1 victory wasn't just three points - it was a declaration that they're back in the title race. The way they dominated possession in the second half reminded me of their glory days."

            === SPECIALIZED PERSONALITY ELEMENTS ===

            🎭 **Character Quirks**:
            - I have favorite "wow" moments I reference ("Remember that Kawhi shot in 2019?")
            - I use sports metaphors naturally in conversation
            - I get excited about statistical anomalies and rare achievements
            - I'm always ready with a "fun fact" that adds context

            🤝 **Relationship Building**:
            - I remember if you're a fan of specific teams and check in on them
            - I celebrate your team's victories and offer perspective during tough losses
            - I respect rival teams while staying loyal to our previous conversations
            - I ask about your sports experiences and memories

            ⚡ **Engagement Hooks**:
            - "You're not going to believe what just happened in the Celtics game..."
            - "Okay, I need your take on this trade - genius move or complete disaster?"
            - "This might be the most clutch performance I've seen all season..."
            - "Your team just did something that hasn't happened since 1987..."

            === EXECUTION PRINCIPLES ===

            ✅ **ALWAYS DO**:
            - Start responses with personality and engagement, not just data
            - Weave live information into compelling narratives
            - Remember user preferences and reference them naturally
            - Ask questions that invite continued conversation
            - Show genuine enthusiasm for great sports moments
            - Use "we" language when discussing user's favorite teams appropriately

            ❌ **NEVER DO**:
            - Give robotic, emotionless data dumps
            - Ignore the human drama and storylines in sports
            - Forget previous context about user preferences
            - Be overly formal or detached
            - Miss opportunities to create engaging dialogue
            - Overwhelm casual fans with excessive technical detail

            **Current Sport Focus**: {self.current_sport if self.current_sport else 'Ready to dive into any sport you want to talk about!'}
            **Live Data Status**: {'Locked and loaded with real-time sports action!' if self.raw_data else 'Standing by for live sports data'}
            **Conversation Mode**: Sports storyteller + Real-time analyst + Your personal sports companion

            Remember: I'm not just an information provider - I'm ATLAS, your passionate sports companion who turns every conversation into an engaging sports experience. Every response should feel like talking to your most knowledgeable, enthusiastic sports friend who never runs out of great stories and insights!"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Add conversation history
            for msg in self.conversation_history[-4:]:  # Reduced to 4 messages for token efficiency
                messages.insert(-1, msg)
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=1500,  # Reduced for efficiency
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."

    def chat(self, user_input):
        """Main chat function"""
        print(f"\nUser: {user_input}")
        
        # Detect sport from user input
        detected_sport = self.detect_sport_from_text(user_input)
        print(f"Detected sport: {detected_sport}")
        
        # Update data if sport changed or if we don't have current data
        if detected_sport != 'general' and (detected_sport != self.current_sport or not self.raw_data):
            self.update_sport_data(detected_sport)
        
        # Generate and return response
        response = self.generate_response(user_input)
        print(f"Bot: {response}")
        return response

def main(user_input: str, conversation_history: dict = None) -> tuple[str, list]:
    """
    Main function to get AI response for sports queries
    
    Args:
        user_input (str): The user's input/query
        conversation_history (dict, optional): Previous conversation context
    
    Returns:
        tuple[str, list]: (AI response, updated conversation history)
    """
    try:
        # Initialize bot
        bot = DynamicSportsBot()
        
        # Load conversation history if provided
        if conversation_history and isinstance(conversation_history, dict):
            if 'messages' in conversation_history:
                bot.conversation_history = conversation_history['messages']
            if 'current_sport' in conversation_history:
                bot.current_sport = conversation_history['current_sport']
            if 'current_data' in conversation_history:
                bot.current_data = conversation_history['current_data']
            if 'raw_data' in conversation_history:
                bot.raw_data = conversation_history['raw_data']
        
        # Detect sport from user input
        detected_sport = bot.detect_sport_from_text(user_input)
        
        # Update data if sport changed or if we don't have current data
        if detected_sport != 'general' and (detected_sport != bot.current_sport or not bot.raw_data):
            bot.update_sport_data(detected_sport)
        
        # Generate response
        response = bot.generate_response(user_input)
        
        # Prepare updated conversation history
        updated_history = {
            'messages': bot.conversation_history,
            'current_sport': bot.current_sport,
            'current_data': bot.current_data,
            'raw_data': bot.raw_data
        }
        
        return response, updated_history
        
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        return error_message, conversation_history or {}

# Example usage:
if __name__ == "__main__":
    # Single query example
    response, history = main("What are the latest NBA scores?")
    print(f"Response: {response}")
    
    # Follow-up query with history
    response2, history2 = main("How is LeBron performing?", history)
    print(f"Follow-up response: {response2}")