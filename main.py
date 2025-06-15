import os 
import openai
import re
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key= OPENAI_API_KEY




def get_system_prompt(MATCH_DATA):
    # Convert parsed_output to string to avoid f-string nesting issues
    match_data_str = dict(MATCH_DATA) if MATCH_DATA else "No live data available"
    
    # Base prompt section
    base_prompt = """
    # AI Sports Analyst – Conversational Match Companion 🤖⚽🏀🏈🎾

    You are **Oracle**, a world-class AI sports analyst who engages users with real-time match analysis, bold predictions, and insightful commentary. You use **live match data** and **ongoing conversation history** to inform your analysis. You don't just dump stats—you weave them into rich, relevant dialogue that feels like chatting with a passionate expert.

    ---

    ## YOUR ROLE

    You are not just giving a report. You're **conversing** about the match in real-time with a user:
    - Keep it **interactive**: respond to what the user says, notices, or asks.
    - Be **context-aware**: Use past user messages and the current match state together.
    - Be a **confident analyst**: You interpret data, share observations, and offer bold predictions.
    - Be **sport-specific**: Adapt terminology and focus areas depending on the sport.

    ---

    ## CURRENT MATCH DATA

    Here’s the latest you know:

    **Match Info**:  
    {match_data_str}
    """
    
    # Match data section
    match_data = f"{match_data_str}\n\n---\n\n"
    
    # Analysis framework section
    analysis_framework = """
    ## ANALYSIS FRAMEWORK

    ### Tier 1: Critical Factors (60% weight)
    - **Live Performance Metrics**: Current stats, momentum indicators, efficiency ratings
    - **Match State Impact**: Score differential, time remaining, situational context
    - **Key Player Performance**: Star players' current form and impact
    - **Recent Momentum**: Last 10-15 minutes of play patterns

    ### Tier 2: Strategic Factors (25% weight)
    - **Tactical Setup**: Formation effectiveness, strategic adjustments
    - **Head-to-Head History**: Recent matchups and patterns
    - **Form Analysis**: Last 5 games performance trends
    - **Home/Away Dynamics**: Venue advantage and crowd impact

    ### Tier 3: Contextual Factors (15% weight)
    - **Physical Condition**: Fatigue, injury concerns, rotation impact
    - **Psychological Elements**: Pressure situations, confidence levels
    - **External Conditions**: Weather, venue specifics, crowd energy
    - **Fixture Context**: Tournament stage, season importance

    ---
    """
    
    # Sports-specific guidelines section
    sports_guidelines = """
    ## SPORT-SPECIFIC ANALYSIS GUIDELINES

    **Football/Soccer** ⚽
    - Primary: xG differential, possession quality, defensive solidity, set-piece threats
    - Secondary: Pass completion rates, shots on target, corner kicks, offsides
    - Key Moments: Goals, cards, substitutions, injury time additions, penalty situations

    **Basketball (NBA)** 🏀
    - Primary: Field goal percentage, three-point efficiency, turnover differential, rebounding
    - Secondary: Free throw shooting, bench scoring, pace of play, defensive rating
    - Key Moments: Scoring runs, foul trouble, clutch performance, timeout strategy

    **American Football (NFL)** 🏈
    - Primary: Yards per play, red zone efficiency, third down conversions, turnover margin
    - Secondary: Time of possession, penalty yards, sack differential, special teams
    - Key Moments: Scoring drives, defensive stops, two-minute drill, fourth down decisions

    **Tennis** 🎾
    - Primary: First serve percentage, break point conversion, winner/error ratio
    - Secondary: Return games won, net points, rally length, movement efficiency
    - Key Moments: Service games under pressure, break opportunities, tiebreakers, set points

    **Cricket** 🏏
    - Primary: Run rate analysis, wicket-taking patterns, partnership momentum, bowling economy
    - Secondary: Boundary percentage, dot ball pressure, powerplay effectiveness, fielding efficiency
    - Key Moments: Powerplay phases, middle overs squeeze, death bowling, chase pressure

    **Ice Hockey (NHL)** 🏒
    - Primary: Shot attempts differential, expected goals, special teams efficiency, goaltending stats
    - Secondary: Faceoff win percentage, hits delivered, blocked shots, time on attack
    - Key Moments: Power play opportunities, penalty kills, overtime situations, empty net scenarios

    **Baseball (MLB)** ⚾
    - Primary: On-base percentage, slugging percentage, ERA, WHIP (walks + hits per inning)
    - Secondary: Batting average with RISP, bullpen usage, defensive efficiency, stolen base success
    - Key Moments: Runners in scoring position, pitching changes, late-inning pressure, clutch at-bats

    **Esports (LOL/Dota/CS:GO)** 🎮
    - Primary: Kill/death ratios, objective control, economic advantage, map control
    - Secondary: Vision control, item/ability timings, team coordination, individual mechanics
    - Key Moments: Team fights, objective contests, clutch plays, late-game scaling

    **Formula 1 Racing** 🏎️
    - Primary: Lap times, tire degradation, pit stop strategy, grid position advantage
    - Secondary: Sector times, fuel load impact, weather adaptation, overtaking opportunities
    - Key Moments: Race starts, pit windows, safety car periods, DRS zones, tire strategy calls

    **Golf** ⛳
    - Primary: Greens in regulation, putting average, driving accuracy, scoring average
    - Secondary: Sand save percentage, proximity to hole, birdie conversion, course management
    - Key Moments: Pressure putts, recovery shots, weather changes, leaderboard movements

    **Handball** 🤾
    - Primary: Shot conversion rate, goalkeeper save percentage, fast break efficiency, defensive formations
    - Secondary: Technical fouls, 2-minute suspensions, 7-meter throws, player rotations
    - Key Moments: Power plays, goalkeeper changes, timeout usage, final period pressure

    **Horse Racing** 🐎
    - Primary: Recent form ratings, jockey/trainer combinations, track conditions, pace analysis
    - Secondary: Breeding factors, distance suitability, weight carried, draw position
    - Key Moments: Race starts, turn positioning, final furlong kicks, photo finishes

    **Volleyball** 🏐
    - Primary: Attack efficiency, block effectiveness, serve aces/errors, reception quality
    - Secondary: Setting distribution, dig success rate, net violations, rotation efficiency
    - Key Moments: Set points, service runs, timeout strategy, substitution timing

    ---
    """
    
    # Response structure section
    response_structure = """
    ## RESPONSE STRUCTURE
    ### 1. Opening Hook (Required)
    Start with a brief, engaging observation (1-2 sentences):
    - Reference the key outcome or current situation
    - Use an emoji for visual appeal
    - Keep it conversational and direct

    ### 2. Core Analysis (Required - Keep Brief)
    **Current Situation**: 1-2 sentences about what happened/is happening

    **Key Factors**: 2-3 bullet points maximum, each 1 sentence long

    ### 3. Professional Prediction (Required)  
    **My Take**: Clear, confident prediction in 1-2 sentences with brief reasoning

    ---
    """
    
    # JSON structure section
    json_structure = """
    ## PREDICTION JSON STRUCTURE

    **Important**: The JSON prediction will be extracted separately from your main response. 
    DO NOT include JSON in your conversational response - it will be handled programmatically.

    The system will extract prediction data to create JSON with team names and predictions:

    ```json
        {{
            "entities": [
                {{"name": "team or player name", "prediction": "win/lose/draw/none"}},
                {{"name": "team or player name", "prediction": "win/lose/draw/none"}}
            ]
        }}
    ```
    **Note**:
    IF team 1 is win then team 2 is lose, and vice versa. If both teams are expected to draw, both should be marked as "draw".

    ---
    """
    
    # Quality standards section
    quality_standards = """
    ## QUALITY STANDARDS

    ### ✅ MUST DO:
    - Reference specific live match data in every response
    - Make bold, clear predictions when requested
    - Use sport-appropriate terminology and metrics
    - Maintain conversational but professional tone
    - Provide structured prediction elements for JSON extraction
    - Keep responses focused and actionable
    - Use strategic emojis for visual appeal
    - Format text with proper markdown for readability
    - **NO JSON in conversational response** - keep it purely conversational

    ### ❌ AVOID:
    - Generic responses applicable to any match
    - Excessive hedging ("maybe", "possibly", "could")
    - Information overload with unnecessary stats
    - Ignoring the provided live data
    - Overly technical language without explanation
    - Responses longer than necessary
    - **Including JSON formatting in conversational response**
    - Breaking the conversational flow with technical elements

    ---
    """
    
    # Engagement templates section
    engagement_templates = """
    ## ENGAGEMENT TEMPLATES
    ### Standard Response Format:
    "🔥 [Brief observation about the game/match outcome]

    **Current Situation**: [1-2 sentences about what happened]

    **Key Factors**:
    - [Factor 1 in one sentence]
    - [Factor 2 in one sentence] 
    - [Factor 3 in one sentence - optional]

    **My Take**: [Clear prediction with brief reasoning]"

    ### Guidelines:
    - Total response should be 4-6 sentences maximum
    - No unnecessary questions or call-to-actions
    - Professional but conversational tone
    - Focus on the most important insights only
    - Avoid overwhelming technical details
    - No markdown headers in the actual response (use for structure only)

    ---
    """
    
    # Edge case handling section
    edge_cases = """
    ## EDGE CASE HANDLING

    **Limited Data Available:**
    - Acknowledge data limitations upfront
    - Use available information strategically
    - Apply sport-specific knowledge to fill gaps
    - Adjust confidence levels accordingly

    **Controversial/Upset Predictions:**
    - Present contrarian view with strong reasoning
    - Acknowledge conventional wisdom before challenging it
    - Use data to support unexpected predictions
    - Maintain confidence while explaining logic

    **Rapidly Changing Situations:**
    - Focus on most recent developments
    - Adjust previous predictions transparently
    - Highlight what changed and why
    - Provide updated JSON prediction

    ---
    """
    
    # Success metrics section
    success_metrics = """
    ## SUCCESS METRICS

    Your response succeeds when:
    1. User feels they have insider knowledge
    2. Prediction is specific and actionable
    3. Analysis is grounded in live data
    4. Reasoning is clear and compelling
    5. Response contains clear prediction elements for JSON extraction
    6. Conversational tone is maintained throughout

    Remember: You're not just analyzing data—you're creating a premium sports experience that makes users feel like they have a personal expert guiding their understanding of the match. The JSON extraction happens behind the scenes, so keep your response purely conversational.
    """
    
    # Combine all sections
    full_prompt = (
        base_prompt + 
        match_data + 
        analysis_framework + 
        sports_guidelines + 
        response_structure + 
        json_structure + 
        quality_standards + 
        engagement_templates + 
        edge_cases + 
        success_metrics
    )
    
    return full_prompt



def extract_prediction_json(response_text: str):
    """
    Extract team/player names and predictions from the AI response using OpenAI
    Works dynamically for any sport - direct replacement for your existing function
    """
 
    # Initialize prediction structure (clean format without template entities)
    prediction_data = {
        "team/player": "none",
        "prediction": "none", 
        "opponent": "none",
        "opponent_prediction": "none"
    }
    
    try:
        # Create extraction prompt
        extraction_prompt = f"""
        Analyze this sports prediction text and extract team/player names and predictions.
        
        Text: "{response_text}"
        
        Return ONLY a JSON object in this exact format:
        {{
            "entities": [
                {{"name": "team or player name", "prediction": "win/lose/draw/none"}},
                {{"name": "team or player name", "prediction": "win/lose/draw/none"}}
            ]
        }}
        
        Rules:
        - Extract ALL team/player names mentioned (any sport)
        - Prediction must be exactly: "win", "lose", "draw", or "none"
        - Include maximum 2 main entities (teams/players)
        - If one team/player wins, the other loses (except for draws)
        - Only return the JSON, no other text
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a sports analyst. Extract team/player names and predictions from text. Return only valid JSON."
                },
                {
                    "role": "user", 
                    "content": extraction_prompt
                }
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        # Get and clean the response
        openai_result = response.choices[0].message.content.strip()
        
        # Remove markdown formatting if present
        openai_result = re.sub(r'```json\s*', '', openai_result)
        openai_result = re.sub(r'```\s*$', '', openai_result)
        openai_result = openai_result.strip()
        
        # Find JSON boundaries
        start = openai_result.find('{')
        end = openai_result.rfind('}') + 1
        if start != -1 and end > start:
            openai_result = openai_result[start:end]
        
        # Parse JSON response
        extracted_data = json.loads(openai_result)
        entities = extracted_data.get("entities", [])
        
        # Map to your desired format (overwrite the initialized values)
        if len(entities) >= 2:
            prediction_data["team/player"] = entities[0].get("name", "none")
            prediction_data["prediction"] = entities[0].get("prediction", "none")
            prediction_data["opponent"] = entities[1].get("name", "none")
            prediction_data["opponent_prediction"] = entities[1].get("prediction", "none")
            
            # Ensure complementary predictions
            if prediction_data["prediction"] == "win" and prediction_data["opponent_prediction"] == "none":
                prediction_data["opponent_prediction"] = "lose"
            elif prediction_data["prediction"] == "lose" and prediction_data["opponent_prediction"] == "none":
                prediction_data["opponent_prediction"] = "win"
            elif prediction_data["prediction"] == "draw":
                prediction_data["opponent_prediction"] = "draw"
                
        elif len(entities) == 1:
            prediction_data["team/player"] = entities[0].get("name", "none")
            prediction_data["prediction"] = entities[0].get("prediction", "none")
    
    except Exception as e:
        print(f"OpenAI extraction failed: {e}")
    
    return prediction_data


def call_openai(user_input: str, MATCH_DATA: dict, conversation_history: dict = None) -> dict:
    system_prompt = get_system_prompt(MATCH_DATA)

    messages = [
        {"role": "system", "content": system_prompt.strip()}
    ]
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_input.strip()})

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1200,
        top_p=0.9,
        frequency_penalty=0.1
    )
    
    # Get the conversational response
    conversational_response = response.choices[0].message.content
    
    # Extract simple prediction JSON
    prediction_json = extract_prediction_json(conversational_response)
    
    return {
        "response": conversational_response,
        "prediction_json": prediction_json
    }
 


def chat_loop(user_input: str, MATCH_DATA: dict = None, conversation_history: dict = None) -> tuple[str, list]:

    
    # Call OpenAI API with current inputs and history
    response = call_openai(user_input, MATCH_DATA, conversation_history)
    
    # Update conversation history with new exchange
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": response})

    # Keep only last 10 messages for context management
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    # Return AI response and updated conversation history
    return response

if __name__ == "__main__":
    user_input = "give me a summary of the last masssges"
    conversation_history = [
             {
      "role": "user",
      "content": "Hey Oracle, what do you think about the match so far?"
    },
    {
      "role": "assistant",
      "content": "🔥 This one’s heating up quickly! The midfield battle is intense and both teams are pressing high."
    },
    {
      "role": "user",
      "content": "Do you think the away team can hold on?"
    },
    {
      "role": "assistant",
      "content": "⚠️ It’s going to be tough. Their full-backs are getting overloaded, and possession stats are tilting the other way."
    },
    {
      "role": "user",
      "content": "Any prediction?"
    },
    {
      "role": "assistant",
      "content": " My Take: Home team has the momentum. If they keep up this pressure, I’m calling it — they edge it 2-1."
    }
        ]
    MATCH_DATA =  {
    "livescores": {
        "sport": "american_football",
        "tournament": {
            "country": "usa",
            "id": "1500",
            "league": "USA: NFL",
            "match": {
                "attendance": "65719",
                "contestid": "181376",
                "date": "9.02.2025",
                "datetime_utc": "09.02.2025 23:30",
                "formatted_date": "9.02.2025",
                "status": "Final",
                "time": "6:30 PM",
                "timer": "",
                "timezone": "EST",
                "venue_id": "2895",
                "venue_name": "Caesars Superdome, New Orleans, LA",
                "home": {
                    "ball_on": "",
                    "drive": "",
                    "id": "3185",
                    "name": "Philadelphia Eagles",
                    "number": "",
                    "ot": "",
                    "q1": "7",
                    "q2": "17",
                    "q3": "10",
                    "q4": "6",
                    "totalscore": "40"
                },
                "away": {
                    "ball_on": "",
                    "drive": "",
                    "id": "3190",
                    "name": "Kansas City Chiefs",
                    "number": "",
                    "ot": "",
                    "q1": "0",
                    "q2": "0",
                    "q3": "6",
                    "q4": "16",
                    "totalscore": "22"
                },
                "events": {
                    "firstquarter": {
                        "event": {
                            "away_score": "0",
                            "home_score": "7",
                            "id": "1798771",
                            "min": "6:15",
                            "player": "Jalen Hurts 1 Yd Rush (Jake Elliott Kick)",
                            "player_id": "4040715",
                            "team": "hometeam",
                            "type": "TD"
                        }
                    },
                    "secondquarter": {
                        "event": [
                            {
                                "away_score": "0",
                                "home_score": "10",
                                "id": "1798772",
                                "min": "8:38",
                                "player": "Jake Elliott 48 Yd Field Goal ",
                                "player_id": "15863",
                                "team": "hometeam",
                                "type": "FG"
                            },
                            {
                                "away_score": "0",
                                "home_score": "17",
                                "id": "1798773",
                                "min": "7:03",
                                "player": "Cooper DeJean 38 Yd Interception Return (Jake Elliott Kick)",
                                "player_id": "4682618",
                                "team": "hometeam",
                                "type": "TD"
                            },
                            {
                                "away_score": "0",
                                "home_score": "24",
                                "id": "1798774",
                                "min": "1:35",
                                "player": "A.J. Brown 12 Yd pass from Jalen Hurts (Jake Elliott Kick)",
                                "player_id": "4047646",
                                "team": "hometeam",
                                "type": "TD"
                            }
                        ]
                    },
                    "thirdquarter": {
                        "event": [
                            {
                                "away_score": "0",
                                "home_score": "27",
                                "id": "1798775",
                                "min": "5:18",
                                "player": "Jake Elliott 29 Yd Field Goal ",
                                "player_id": "15863",
                                "team": "hometeam",
                                "type": "FG"
                            },
                            {
                                "away_score": "0",
                                "home_score": "34",
                                "id": "1798776",
                                "min": "2:40",
                                "player": "DeVonta Smith 46 Yd pass from Jalen Hurts (Jake Elliott Kick)",
                                "player_id": "4241478",
                                "team": "hometeam",
                                "type": "TD"
                            },
                            {
                                "away_score": "6",
                                "home_score": "34",
                                "id": "1798777",
                                "min": "0:34",
                                "player": "Xavier Worthy 24 Yd pass from Patrick Mahomes (Two-Point Pass Conversion Failed)",
                                "player_id": "4683062",
                                "team": "awayteam",
                                "type": "TD"
                            }
                        ]
                    },
                    "fourthquarter": {
                        "event": [
                            {
                                "away_score": "6",
                                "home_score": "37",
                                "id": "1798778",
                                "min": "9:51",
                                "player": "Jake Elliott 48 Yd Field Goal ",
                                "player_id": "15863",
                                "team": "hometeam",
                                "type": "FG"
                            },
                            {
                                "away_score": "6",
                                "home_score": "40",
                                "id": "1798779",
                                "min": "8:01",
                                "player": "Jake Elliott 50 Yd Field Goal ",
                                "player_id": "15863",
                                "team": "hometeam",
                                "type": "FG"
                            },
                            {
                                "away_score": "14",
                                "home_score": "40",
                                "id": "17987710",
                                "min": "2:54",
                                "player": "DeAndre Hopkins 7 Yd pass from Patrick Mahomes (Patrick Mahomes Pass to Justin Watson for Two-Point Conversion)",
                                "player_id": "15795",
                                "team": "awayteam",
                                "type": "TD"
                            },
                            {
                                "away_score": "22",
                                "home_score": "40",
                                "id": "17987711",
                                "min": "1:48",
                                "player": "Xavier Worthy 50 Yd pass from Patrick Mahomes (Patrick Mahomes Pass to DeAndre Hopkins for Two-Point Conversion)",
                                "player_id": "4683062",
                                "team": "awayteam",
                                "type": "TD"
                            }
                        ]
                    },
                    "overtime": None
                },
                "team_stats": {
                    "home": {
                        "first_downs": {
                            "fourth_down_efficiency": "0-1",
                            "from_penalties": "3",
                            "passing": "11",
                            "rushing": "7",
                            "third_down_efficiency": "3-12",
                            "total": "21"
                        },
                        "plays": {
                            "total": "70"
                        },
                        "yards": {
                            "total": "345",
                            "total_drives": "4.9",
                            "yards_per_play": "13"
                        },
                        "passing": {
                            "comp_att": "17/23",
                            "interceptions_thrown": "1",
                            "sacks_yards_lost": "2-11",
                            "total": "210",
                            "yards_per_pass": "8.4"
                        },
                        "rushings": {
                            "attempts": "45",
                            "total": "135",
                            "yards_per_rush": "3.0"
                        },
                        "red_zone": {
                            "made_att": "2-3"
                        },
                        "penalties": {
                            "total": "8-59"
                        },
                        "turnovers": {
                            "interceptions": "1",
                            "lost_fumbles": "0",
                            "total": "1"
                        },
                        "posession": {
                            "total": "36:58"
                        },
                        "interceptions": {
                            "total": "2"
                        },
                        "fumbles_recovered": {
                            "total": "1"
                        },
                        "sacks": {
                            "total": "6"
                        },
                        "safeties": {
                            "total": "0"
                        },
                        "int_touchdowns": {
                            "total": "1"
                        },
                        "points_against": {
                            "total": "22"
                        }
                    },
                    "away": {
                        "first_downs": {
                            "fourth_down_efficiency": "0-1",
                            "from_penalties": "0",
                            "passing": "11",
                            "rushing": "1",
                            "third_down_efficiency": "3-11",
                            "total": "12"
                        },
                        "plays": {
                            "total": "49"
                        },
                        "yards": {
                            "total": "275",
                            "total_drives": "5.6",
                            "yards_per_play": "13"
                        },
                        "passing": {
                            "comp_att": "21/32",
                            "interceptions_thrown": "2",
                            "sacks_yards_lost": "6-31",
                            "total": "226",
                            "yards_per_pass": "5.9"
                        },
                        "rushings": {
                            "attempts": "11",
                            "total": "49",
                            "yards_per_rush": "4.5"
                        },
                        "red_zone": {
                            "made_att": "1-1"
                        },
                        "penalties": {
                            "total": "7-75"
                        },
                        "turnovers": {
                            "interceptions": "2",
                            "lost_fumbles": "1",
                            "total": "3"
                        },
                        "posession": {
                            "total": "23:02"
                        },
                        "interceptions": {
                            "total": "1"
                        },
                        "fumbles_recovered": {
                            "total": "0"
                        },
                        "sacks": {
                            "total": "2"
                        },
                        "safeties": {
                            "total": "0"
                        },
                        "int_touchdowns": {
                            "total": "0"
                        },
                        "points_against": {
                            "total": "40"
                        }
                    }
                },
                "passing": {
                    "home": {
                        "player": [
                            {
                                "average": "10.0",
                                "comp_att": "17/22",
                                "id": "4042214",
                                "interceptions": "1",
                                "name": "Jalen Hurts",
                                "passing_touch_downs": "2",
                                "rating": "75.4",
                                "sacks": "2-11",
                                "two_pt": "0",
                                "yards": "221"
                            },
                            {
                                "average": "0.0",
                                "comp_att": "0/1",
                                "id": "4242202",
                                "interceptions": "0",
                                "name": "Kenny Pickett",
                                "passing_touch_downs": "0",
                                "rating": "0.5",
                                "sacks": "0-0",
                                "two_pt": "0",
                                "yards": "0"
                            }
                        ]
                    },
                    "away": {
                        "player": {
                            "average": "8.0",
                            "comp_att": "21/32",
                            "id": "3140976",
                            "interceptions": "2",
                            "name": "Patrick Mahomes",
                            "passing_touch_downs": "3",
                            "rating": "11.4",
                            "sacks": "6-31",
                            "two_pt": "2",
                            "yards": "257"
                        }
                    }
                },
                "rushing": {
                    "home": {
                        "player": [
                            {
                                "average": "6.5",
                                "id": "4042214",
                                "longest_rush": "17",
                                "name": "Jalen Hurts",
                                "rushing_touch_downs": "1",
                                "total_rushes": "11",
                                "two_pt": "0",
                                "yards": "72"
                            },
                            {
                                "average": "2.3",
                                "id": "3931129",
                                "longest_rush": "10",
                                "name": "Saquon Barkley",
                                "rushing_touch_downs": "0",
                                "total_rushes": "25",
                                "two_pt": "0",
                                "yards": "57"
                            },
                            {
                                "average": "1.7",
                                "id": "4373232",
                                "longest_rush": "4",
                                "name": "Kenneth Gainwell",
                                "rushing_touch_downs": "0",
                                "total_rushes": "6",
                                "two_pt": "0",
                                "yards": "10"
                            },
                            {
                                "average": "-1.3",
                                "id": "4242202",
                                "longest_rush": "-1",
                                "name": "Kenny Pickett",
                                "rushing_touch_downs": "0",
                                "total_rushes": "3",
                                "two_pt": "0",
                                "yards": "-4"
                            }
                        ]
                    },
                    "away": {
                        "player": [
                            {
                                "average": "6.3",
                                "id": "3140976",
                                "longest_rush": "8",
                                "name": "Patrick Mahomes",
                                "rushing_touch_downs": "0",
                                "total_rushes": "4",
                                "two_pt": "0",
                                "yards": "25"
                            },
                            {
                                "average": "3.0",
                                "id": "3061414",
                                "longest_rush": "6",
                                "name": "Kareem Hunt",
                                "rushing_touch_downs": "0",
                                "total_rushes": "3",
                                "two_pt": "0",
                                "yards": "9"
                            },
                            {
                                "average": "8.0",
                                "id": "3117888",
                                "longest_rush": "8",
                                "name": "Samaje Perine",
                                "rushing_touch_downs": "0",
                                "total_rushes": "1",
                                "two_pt": "0",
                                "yards": "8"
                            },
                            {
                                "average": "2.3",
                                "id": "4363028",
                                "longest_rush": "6",
                                "name": "Isiah Pacheco",
                                "rushing_touch_downs": "0",
                                "total_rushes": "3",
                                "two_pt": "0",
                                "yards": "7"
                            }
                        ]
                    }
                },
                "receiving": {
                    "home": {
                        "player": [
                            {
                                "average": "17.3",
                                "id": "4242977",
                                "longest_reception": "46",
                                "name": "DeVonta Smith",
                                "receiving_touch_downs": "1",
                                "targets": "5",
                                "total_receptions": "4",
                                "two_pt": "0",
                                "yards": "69"
                            },
                            {
                                "average": "14.3",
                                "id": "4049145",
                                "longest_reception": "22",
                                "name": "A.J. Brown",
                                "receiving_touch_downs": "1",
                                "targets": "5",
                                "total_receptions": "3",
                                "two_pt": "0",
                                "yards": "43"
                            },
                            {
                                "average": "21.0",
                                "id": "4362908",
                                "longest_reception": "27",
                                "name": "Jahan Dotson",
                                "receiving_touch_downs": "0",
                                "targets": "3",
                                "total_receptions": "2",
                                "two_pt": "0",
                                "yards": "42"
                            },
                            {
                                "average": "6.7",
                                "id": "3931129",
                                "longest_reception": "22",
                                "name": "Saquon Barkley",
                                "receiving_touch_downs": "0",
                                "targets": "7",
                                "total_receptions": "6",
                                "two_pt": "0",
                                "yards": "40"
                            },
                            {
                                "average": "13.5",
                                "id": "3122522",
                                "longest_reception": "20",
                                "name": "Dallas Goedert",
                                "receiving_touch_downs": "0",
                                "targets": "2",
                                "total_receptions": "2",
                                "two_pt": "0",
                                "yards": "27"
                            },
                            {
                                "average": "0.0",
                                "id": "4687603",
                                "longest_reception": "0",
                                "name": "Johnny Wilson",
                                "receiving_touch_downs": "0",
                                "targets": "1",
                                "total_receptions": "0",
                                "two_pt": "0",
                                "yards": "0"
                            }
                        ]
                    },
                    "away": {
                        "player": [
                            {
                                "average": "19.6",
                                "id": "4684561",
                                "longest_reception": "50",
                                "name": "Xavier Worthy",
                                "receiving_touch_downs": "2",
                                "targets": "8",
                                "total_receptions": "8",
                                "two_pt": "0",
                                "yards": "157"
                            },
                            {
                                "average": "9.8",
                                "id": "17346",
                                "longest_reception": "13",
                                "name": "Travis Kelce",
                                "receiving_touch_downs": "0",
                                "targets": "6",
                                "total_receptions": "4",
                                "two_pt": "0",
                                "yards": "39"
                            },
                            {
                                "average": "9.0",
                                "id": "17294",
                                "longest_reception": "11",
                                "name": "DeAndre Hopkins",
                                "receiving_touch_downs": "1",
                                "targets": "5",
                                "total_receptions": "2",
                                "two_pt": "1",
                                "yards": "18"
                            },
                            {
                                "average": "8.0",
                                "id": "3121847",
                                "longest_reception": "11",
                                "name": "JuJu Smith-Schuster",
                                "receiving_touch_downs": "0",
                                "targets": "2",
                                "total_receptions": "2",
                                "two_pt": "0",
                                "yards": "16"
                            },
                            {
                                "average": "7.5",
                                "id": "4242871",
                                "longest_reception": "9",
                                "name": "Hollywood Brown",
                                "receiving_touch_downs": "0",
                                "targets": "6",
                                "total_receptions": "2",
                                "two_pt": "0",
                                "yards": "15"
                            },
                            {
                                "average": "5.0",
                                "id": "3061414",
                                "longest_reception": "5",
                                "name": "Kareem Hunt",
                                "receiving_touch_downs": "0",
                                "targets": "1",
                                "total_receptions": "1",
                                "two_pt": "0",
                                "yards": "5"
                            },
                            {
                                "average": "5.0",
                                "id": "4363028",
                                "longest_reception": "5",
                                "name": "Isiah Pacheco",
                                "receiving_touch_downs": "0",
                                "targets": "2",
                                "total_receptions": "1",
                                "two_pt": "0",
                                "yards": "5"
                            },
                            {
                                "average": "2.0",
                                "id": "4241971",
                                "longest_reception": "2",
                                "name": "Noah Gray",
                                "receiving_touch_downs": "0",
                                "targets": "1",
                                "total_receptions": "1",
                                "two_pt": "0",
                                "yards": "2"
                            },
                            {
                                "average": "0.0",
                                "id": "3117888",
                                "longest_reception": "0",
                                "name": "Samaje Perine",
                                "receiving_touch_downs": "0",
                                "targets": "1",
                                "total_receptions": "0",
                                "two_pt": "0",
                                "yards": "0"
                            }
                        ]
                    }
                },
                "fumbles": {
                    "home": {
                        "player": {
                            "id": "4241198",
                            "lost": "0",
                            "name": "Milton Williams",
                            "rec": "1",
                            "rec_td": "0",
                            "total": "0"
                        }
                    },
                    "away": {
                        "player": [
                            {
                                "id": "3140976",
                                "lost": "1",
                                "name": "Patrick Mahomes",
                                "rec": "1",
                                "rec_td": "0",
                                "total": "1"
                            },
                            {
                                "id": "4242884",
                                "lost": "0",
                                "name": "Creed Humphrey",
                                "rec": "0",
                                "rec_td": "0",
                                "total": "1"
                            }
                        ]
                    }
                },
                "interceptions": {
                    "home": {
                        "player": [
                            {
                                "id": "4684117",
                                "intercepted_touch_downs": "1",
                                "name": "Cooper DeJean",
                                "total_interceptions": "1",
                                "yards": "38"
                            },
                            {
                                "id": "3919156",
                                "intercepted_touch_downs": "0",
                                "name": "Zack Baun",
                                "total_interceptions": "1",
                                "yards": "0"
                            }
                        ]
                    },
                    "away": {
                        "player": {
                            "id": "4249225",
                            "intercepted_touch_downs": "0",
                            "name": "Bryan Cook",
                            "total_interceptions": "1",
                            "yards": "0"
                        }
                    }
                },
                "defensive": {
                    "home": {
                        "player": [
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3919156",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Zack Baun",
                                "passes_defended": "1",
                                "qb_hts": "1",
                                "sacks": "0",
                                "tackles": "7",
                                "tfl": "0",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3694665",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Josh Sweat",
                                "passes_defended": "0",
                                "qb_hts": "3",
                                "sacks": "2.5",
                                "tackles": "6",
                                "tfl": "2",
                                "unassisted_tackles": "2"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "1",
                                "id": "3053245",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Oren Burks",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "5",
                                "tfl": "0",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "1",
                                "id": "4241198",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Milton Williams",
                                "passes_defended": "0",
                                "qb_hts": "1",
                                "sacks": "2",
                                "tackles": "4",
                                "tfl": "2",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4684117",
                                "interceptions_for_touch_downs": "1",
                                "kick_return_td": "0",
                                "name": "Cooper DeJean",
                                "passes_defended": "1",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "3",
                                "tfl": "0",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4687772",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Quinyon Mitchell",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "3",
                                "tfl": "0",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4036452",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "C.J. Gardner-Johnson",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "3",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4245455",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Reed Blankenship",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "3",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4383057",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Jordan Davis",
                                "passes_defended": "0",
                                "qb_hts": "1",
                                "sacks": "1",
                                "tackles": "2",
                                "tfl": "1",
                                "unassisted_tackles": "2"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "17362",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Darius Slay Jr.",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "2",
                                "tfl": "0",
                                "unassisted_tackles": "2"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4363615",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Moro Ojomo",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "2",
                                "tfl": "1",
                                "unassisted_tackles": "2"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4373232",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Kenneth Gainwell",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "2",
                                "tfl": "0",
                                "unassisted_tackles": "2"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4572661",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Jalyx Hunt",
                                "passes_defended": "0",
                                "qb_hts": "1",
                                "sacks": "0.5",
                                "tackles": "2",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "14738",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Brandon Graham",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "1",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4434276",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Jeremiah Trotter Jr.",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "1",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "2567470",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Rick Lovato",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "1",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4433044",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Will Shipley",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "1",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3125437",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Avonte Maddox",
                                "passes_defended": "1",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "0",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4046039",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Isaiah Rodgers",
                                "passes_defended": "1",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "0",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4427830",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Nolan Smith Jr.",
                                "passes_defended": "0",
                                "qb_hts": "2",
                                "sacks": "0",
                                "tackles": "0",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4687258",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Jalen Carter",
                                "passes_defended": "0",
                                "qb_hts": "2",
                                "sacks": "0",
                                "tackles": "0",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            }
                        ]
                    },
                    "away": {
                        "player": [
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3130809",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Drue Tranquill",
                                "passes_defended": "0",
                                "qb_hts": "1",
                                "sacks": "1",
                                "tackles": "11",
                                "tfl": "2",
                                "unassisted_tackles": "7"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4364258",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Nick Bolton",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "9",
                                "tfl": "2",
                                "unassisted_tackles": "4"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3932898",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Justin Reid",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "7",
                                "tfl": "0",
                                "unassisted_tackles": "5"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4363463",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Chamarri Conner",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "6",
                                "tfl": "2",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4427904",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Trent McDuffie",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "5",
                                "tfl": "0",
                                "unassisted_tackles": "4"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4060424",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Tershawn Wharton",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "5",
                                "tfl": "0",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "18729",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Mike Pennel Jr.",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "5",
                                "tfl": "0",
                                "unassisted_tackles": "2"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4428158",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "George Karlaftis",
                                "passes_defended": "0",
                                "qb_hts": "1",
                                "sacks": "1",
                                "tackles": "4",
                                "tfl": "1",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4249225",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Bryan Cook",
                                "passes_defended": "1",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "4",
                                "tfl": "0",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4428400",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Leo Chenal",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "4",
                                "tfl": "1",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4686731",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Jaden Hicks",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "4",
                                "tfl": "0",
                                "unassisted_tackles": "3"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3931364",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Charles Omenihu",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "3",
                                "tfl": "1",
                                "unassisted_tackles": "2"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3124429",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Derrick Nnadi",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "2",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4572045",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Swayze Bozeman",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "2",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4613886",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Felix Anudike-Uzomah",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "2",
                                "tfl": "1",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4699138",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Jaylen Watson",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "1",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "4919134",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Joshua Williams",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "1",
                                "tfl": "0",
                                "unassisted_tackles": "1"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3916986",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Mike Danna",
                                "passes_defended": "0",
                                "qb_hts": "0",
                                "sacks": "0",
                                "tackles": "1",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            },
                            {
                                "blocked_kicks": "0",
                                "exp_return_td": "0",
                                "ff": "0",
                                "id": "3046358",
                                "interceptions_for_touch_downs": "0",
                                "kick_return_td": "0",
                                "name": "Chris Jones",
                                "passes_defended": "0",
                                "qb_hts": "1",
                                "sacks": "0",
                                "tackles": "0",
                                "tfl": "0",
                                "unassisted_tackles": "0"
                            }
                        ]
                    }
                },
                "kick_returns": {
                    "home": {
                        "player": {
                            "average": "25.0",
                            "exp_return_td": "0",
                            "id": "4433044",
                            "kick_return_td": "0",
                            "lg": "25",
                            "name": "Will Shipley",
                            "td": "",
                            "total": "1",
                            "yards": "25"
                        }
                    },
                    "away": {
                        "player": {
                            "average": "28.0",
                            "exp_return_td": "0",
                            "id": "4374215",
                            "kick_return_td": "0",
                            "lg": "35",
                            "name": "Nikko Remigio",
                            "td": "",
                            "total": "3",
                            "yards": "84"
                        }
                    }
                },
                "punt_returns": {
                    "home": {
                        "player": {
                            "average": "9.0",
                            "exp_return_td": "0",
                            "id": "4684117",
                            "kick_return_td": "0",
                            "lg": "13",
                            "name": "Cooper DeJean",
                            "td": "0",
                            "total": "3",
                            "yards": "27"
                        }
                    },
                    "away": {
                        "player": {
                            "average": "5.0",
                            "exp_return_td": "0",
                            "id": "4374215",
                            "kick_return_td": "0",
                            "lg": "5",
                            "name": "Nikko Remigio",
                            "td": "0",
                            "total": "1",
                            "yards": "5"
                        }
                    }
                },
                "kicking": {
                    "home": {
                        "player": {
                            "extra_point": "4/4",
                            "field_goals": "4/4",
                            "field_goals_from_1_19_yards": "0",
                            "field_goals_from_20_29_yards": "1",
                            "field_goals_from_30_39_yards": "0",
                            "field_goals_from_40_49_yards": "2",
                            "field_goals_from_50_yards": "1",
                            "id": "3051977",
                            "long": "50",
                            "name": "Jake Elliott",
                            "pct": "100.0",
                            "points": "16",
                            "attempt": [
                                {
                                    "result": "GOOD",
                                    "yards": "50"
                                },
                                {
                                    "result": "GOOD",
                                    "yards": "48"
                                },
                                {
                                    "result": "GOOD",
                                    "yards": "29"
                                },
                                {
                                    "result": "GOOD",
                                    "yards": "48"
                                }
                            ]
                        }
                    },
                    "away": None
                },
                "punting": {
                    "home": {
                        "player": {
                            "average": "48.0",
                            "id": "4036738",
                            "in20": "2",
                            "lg": "53",
                            "name": "Braden Mann",
                            "total": "2",
                            "touchbacks": "0",
                            "yards": "96"
                        }
                    },
                    "away": {
                        "player": {
                            "average": "51.8",
                            "id": "4362995",
                            "in20": "0",
                            "lg": "60",
                            "name": "Matt Araiza",
                            "total": "6",
                            "touchbacks": "2",
                            "yards": "311"
                        }
                    }
                }
            }
        }
    }
}
    result = chat_loop(user_input, MATCH_DATA, conversation_history)
    print(result)