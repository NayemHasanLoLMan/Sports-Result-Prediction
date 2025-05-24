
                                          #test-1 Getting driver details (working perfectly)

# import http.client
# import json

# # Replace with your actual API key
# API_KEY = "09764d670259f4c5d347028e5e1a629e"
# HOST = "v1.formula-1.api-sports.io"
# HEADERS = {
#     'x-rapidapi-host': HOST,
#     'x-rapidapi-key': API_KEY
# }

# def fetch_driver_profile(name='verstappen'):
#     conn = http.client.HTTPSConnection(HOST)
#     conn.request("GET", f"/drivers?search={name}", headers=HEADERS)
#     res = conn.getresponse()
#     data = res.read().decode("utf-8")
#     return json.loads(data)

# # Fetch Max Verstappen's profile
# driver_data = fetch_driver_profile()
# driver = driver_data["response"][0]

# # === Driver Basic Info ===
# print("\n=== Max Verstappen – Driver Profile ===")
# print(f"🆔 ID: {driver['id']}")
# print(f"🏁 Name: {driver['name']}")
# print(f"🇳🇱 Nationality: {driver['nationality']}")
# print(f"🎂 Birthdate: {driver['birthdate']}")
# print(f"📍 Birthplace: {driver['birthplace']}")
# print(f"🚗 Number: {driver.get('number', 'N/A')}")
# print(f"🏆 World Championships: {driver['world_championships']}")
# print(f"🥇 Highest Finish: P{driver['highest_race_finish']['position']} ({driver['highest_race_finish']['number']} times)")
# print(f"🎖️ Podiums: {driver['podiums']}")
# print(f"🏁 Grands Prix Entered: {driver['grands_prix_entered']}")
# print(f"💯 Career Points: {driver['career_points']}")
# print(f"🖼️ Image: {driver['image']}")

# # === Team History ===
# print("\n=== Team History by Season ===")
# teams = driver.get("teams", [])
# for team_entry in sorted(teams, key=lambda x: x["season"], reverse=True):
#     season = team_entry["season"]
#     team_name = team_entry["team"]["name"]
#     team_logo = team_entry["team"]["logo"]
#     print(f"📅 {season} → {team_name}")

                                                 


                                    #test-2 finding race data



import http.client
import json
from datetime import datetime

API_KEY = "09764d670259f4c5d347028e5e1a629e"  # Replace with your API key
HOST = "v1.formula-1.api-sports.io"
HEADERS = {
    'x-rapidapi-host': HOST,
    'x-rapidapi-key': API_KEY
}

def fetch_data(endpoint):
    conn = http.client.HTTPSConnection(HOST)
    conn.request("GET", endpoint, headers=HEADERS)
    res = conn.getresponse()
    return json.loads(res.read().decode("utf-8"))

def find_race_id(season, race_keyword):
    print(f"🔍 Searching for race in {season} containing '{race_keyword}'...")
    data = fetch_data(f"/races?season={season}")
    for race in data["response"]:
        name = race["competition"]["name"].lower()
        circuit = race["circuit"]["name"].lower()
        if race_keyword.lower() in name or race_keyword.lower() in circuit:
            race_id = race["id"]
            print(f"✅ Found: {name} at {circuit} (Race ID: {race_id})")
            return race_id
    print("❌ Race not found.")
    return None

def print_race_results(race_id):
    print("\n📊 Race Results")
    data = fetch_data(f"/rankings/races?race={race_id}")
    for entry in data["response"]:
        driver = entry["driver"]["name"]
        team = entry["team"]["name"]
        pos = entry["position"]
        time = entry.get("time", "N/A")
        points = entry.get("points", 0)
        print(f"🏁 {pos}. {driver} – {team} | ⏱️ Time: {time} | 🏆 Points: {points}")

def print_starting_grid(race_id):
    print("\n🏁 Starting Grid")
    data = fetch_data(f"/rankings/startinggrid?race={race_id}")
    for entry in data["response"]:
        grid_pos = entry["position"]
        driver = entry["driver"]["name"]
        team = entry["team"]["name"]
        print(f"🔢 {grid_pos}: {driver} – {team}")

def print_fastest_laps(race_id):
    print("\n⚡ Fastest Laps")
    data = fetch_data(f"/rankings/fastestlaps?race={race_id}")
    for entry in data["response"]:
        driver = entry["driver"]["name"]
        lap_time = entry["time"]
        rank = entry["position"]
        print(f"🏎️ {rank}. {driver} – ⏱️ {lap_time}")

def print_pitstops(race_id):
    print("\n🛑 Pit Stops")
    data = fetch_data(f"/pitstops?race={race_id}")
    for entry in data["response"]:
        driver = entry["driver"]["name"]
        stop_num = entry.get("stop", "N/A")
        lap = entry.get("lap", "N/A")
        time = entry.get("time", "N/A")
        print(f"🛠️ Lap {lap}: {driver} – Stop #{stop_num} | ⏱️ {time}")



# === MAIN ===
season = 2023
race_keyword = "monaco"

race_id = find_race_id(season, race_keyword)

if race_id:
    print_race_results(race_id)
    print_starting_grid(race_id)
    print_fastest_laps(race_id)
    print_pitstops(race_id)
else:
    print("❌ Aborting – No race found.")


