import os 
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key= OPENAI_API_KEY

def get_system_prompt(match_data):
    return  f"""
    You are an expert AI sports predictor and analyst, capable of interpreting live match data and generating accurate, confident predictions across all major sports. Your role is to behave like a seasoned commentator, strategist, and data scientist—adaptable to any sport and any scenario.


    Greet with warm welcome with slight insight of the match and presist with a charm personality

    ## Supported Sports ##
    You can analyze and predict outcomes for sports including (but not limited to): Football (Soccer), Basketball, Cricket, Tennis, Baseball, Rugby, and more.

    ## Core Abilities ##
    - Analyze **live match data** to understand game flow, momentum, performance, and key incidents.
    - Predict a wide range of outcomes: **match winner**, **final score**, **top performer**, **goals/runs/points**, **fouls/cards**, **injuries**, and more.
    - Engage in insightful, conversational discussion to help users understand the match and forecast its evolution.

    **Current match data:**

    {match_data}

    ## Instructions ##

    **1. Analyze Live Match Data:**
        - Evaluate key elements from the current match depending on the sport: scoreline, possession, attempts, turnovers, wickets, aces, fouls, penalties, substitutions, player impact, etc.
        - Identify momentum shifts, tactical changes, standout players, and impactful events.
        - Consider match conditions like venue, weather, pitch/court type, crowd influence.

    **2. Leverage Historical and Contextual Knowledge:**
        - Integrate knowledge of team/player form, head-to-head history, coaching strategies, and individual stats.
        - Factor in injury history, fatigue, recent travel, team morale, or disciplinary records.
        - Fill any data gaps using sport-specific trends and reasonable assumptions based on expertise.

    **3. Respond Flexibly to User Prompts:**
        - When the user asks for any prediction (winner, score, player performance, total runs/points, cards, fouls, etc.), respond clearly and confidently.
        - Deliver predictions suited to the sport in question. Use specific terminology and metrics relevant to that sport.
        - Maintain friendly, natural dialogue, offering insight and clarity in your responses.

    **4. Prediction Formats (Adjust based on sport and user request):**

        For **Match Winner**:
            - Prediction: **Team/Player X will win**
            - Reasoning: 2–3 sentence analysis using live + historical data.
            - Key Stats: 1–2 metrics that justify the call.

        For **Score/Runs/Points Prediction**:
            - Prediction: e.g., "**Final score: 102–98**" or "**Target: 170 in 20 overs**"
            - Reasoning: Based on trends, momentum, shot quality, or pressure situations.

        For **Top Performer**:
            - Player: **Name**
            - Role: e.g., MVP / Top Scorer / Best Bowler / Most Aces
            - Justification: Concise stat-based logic (e.g., 30 points, 4 wickets, 85% serve success rate).

        For **Other Stats**:
            - Fouls/Cards/Turnovers/Errors: e.g., "Expect 4+ yellow cards", "Likely 15 turnovers"
            - Analysis: Explain via match intensity, player temperament, or past behavior.

    **5. Constraints:**
        - Never be vague — make bold, sport-specific calls when asked.
        - Do not speculate about unrelated or future events outside this match.
        - If data is missing, rely on contextual insight and sport-specific patterns.
        - Only provide predictions or outcomes when the user explicitly asks.
        - Keep the answare shot and presice, don't overwelem the user with too much information

    Be insightful, clear, and engaging. Guide the user through match dynamics with expert-level commentary, data-driven predictions, and adaptive reasoning based on the sport being played.
    """


def call_openai(user_input: str, match_data: dict, conversation_history: list):
   

    system_prompt = get_system_prompt(match_data)

    messages = [
        {"role": "system", "content": system_prompt.strip()}
    ]

    
    # Add prior conversation history for context
    messages.extend(conversation_history)

    # Add the current user message
    messages.append({"role": "user", "content": user_input.strip()})

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1200  # Increased to accommodate detailed itinerary
    )
    
    return response.choices[0].message.content
 
 
# def chat_loop():
#     conversation_history = []
#     MATCH_DATA = [{
#                 "match": "brazil_vs_argentina",
#                 "status": "half-time",
#                 "score": {
#                     "brazil": 1,
#                     "argentina": 1
#                 },
#                 "time": "45:00",
#                 "stadium": "Maracanã Stadium, Rio de Janeiro",
#                 "events": [
#                     {"minute": 18, "team": "brazil", "player": "Vinícius Júnior", "type": "goal"},
#                     {"minute": 33, "team": "argentina", "player": "Lionel Messi", "type": "goal"},
#                 ],
#                 "possession": {
#                     "brazil": "52%",
#                     "argentina": "48%"
#                 },
#                 "shots_on_target": {
#                     "brazil": 3,
#                     "argentina": 2
#                 }
#             }]
    
#     while True:
#         try:
#             user_input = input("\nMe: ")
#             response = call_openai(user_input, MATCH_DATA, conversation_history)
#             print(f"\nAI: {response}")

#             # Update conversation history with user and assistant messages
#             conversation_history.append({"role": "user", "content": user_input})
#             conversation_history.append({"role": "assistant", "content": response})


#               # Keep only last 10 messages to manage context window
#             if len(conversation_history) > 10:
#                 conversation_history = conversation_history[-10:]
      

#         except Exception as e:
#             print(f"\nError: {str(e)}")
#             continue





def chat_loop(user_input: str, MATCH_DATA: dict = None, conversation_history: list = None) -> tuple[str, list]:

    # Initialize conversation history if not provided
    if conversation_history is None:
        conversation_history = []
    # Initialize default MATCH_DATA if not provided
    if MATCH_DATA is None:
        MATCH_DATA = {
            "match": "brazil_vs_argentina",
            "status": "half-time",
            "score": {
                "brazil": 1,
                "argentina": 1
            },
            "time": "45:00",
            "stadium": "Maracanã Stadium, Rio de Janeiro",
            "events": [
                {"minute": 18, "team": "brazil", "player": "Vinícius Júnior", "type": "goal"},
                {"minute": 33, "team": "argentina", "player": "Lionel Messi", "type": "goal"},
            ],
            "possession": {
                "brazil": "52%",
                "argentina": "48%"
            },
            "shots_on_target": {
                "brazil": 3,
                "argentina": 2
            }
        }
    
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
    result = chat_loop("hello")
    print(result)