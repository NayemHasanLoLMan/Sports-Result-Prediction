import json

# The JSON data you provided (this is just a snippet, as it's very large)
json_data ={
{
    "scores": {
        "sport": "cricket",
        "updated": "11.06.2025 22:06:14",
        "category": [
            {
                "id": "5536",
                "name": "ICC World Test Championship - Test",
                "match": {
                    "date": "11.06.2025",
                    "date_range": "11.06.2025-15.06.2025",
                    "formatted_date": "11.06.2025-15.06.2025",
                    "id": "13072004363",
                    "status": "Stumps",
                    "time": "09:30",
                    "type": "TEST",
                    "venue": "Lord's, London",
                    "home": {
                        "id": "3901",
                        "name": "Australia",
                        "stat": "",
                        "totalscore": "212",
                        "winner": "False"
                    },
                    "away": {
                        "id": "3931",
                        "name": "South Africa",
                        "stat": "",
                        "totalscore": "43/4",
                        "winner": "False"
                    },
                    "comment": {
                        "first_batting_teamid": "2402",
                        "post": "Day 1 - South Africa trail by 169 runs.",
                        "toss_winner_teamid": "2432"
                    },
                    "inning": [
                        {
                            "inningnum": "1",
                            "name": "Australia 1 INN",
                            "team": "localteam",
                            "batsmanstats": {
                                "player": [
                                    {
                                        "b": "20",
                                        "bat": "False",
                                        "batsman": "UT Khawaja",
                                        "dismissal_bowler": "550215",
                                        "dismissal_type": "caught",
                                        "dots": "",
                                        "id": "2993",
                                        "profileid": "215155",
                                        "r": "0",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "0",
                                        "status": "c Bedingham b Rabada",
                                        "dismissal_fielders": {
                                            "dismissal_fielder": {
                                                "name": "DG Bedingham",
                                                "profileid": "498585"
                                            }
                                        }
                                    },
                                    {
                                        "b": "13",
                                        "bat": "False",
                                        "batsman": "AT Carey",
                                        "dismissal_bowler": "267724",
                                        "dismissal_type": "bowled",
                                        "dots": "",
                                        "id": "8335",
                                        "profileid": "326434",
                                        "r": "23",
                                        "s4": "4",
                                        "s6": "0",
                                        "sr": "74.19",
                                        "status": "b Maharaj",
                                        "dismissal_fielders": null
                                    }
                                ]
                            }
                        },
                        {
                            "inningnum": "2",
                            "name": "South Africa 1 INN",
                            "team": "visitorteam",
                            "batsmanstats": {
                                "player": [
                                    {
                                        "b": "6",
                                        "bat": "False",
                                        "batsman": "AK Markram",
                                        "dismissal_bowler": "311592",
                                        "dismissal_type": "bowled",
                                        "dots": "",
                                        "id": "10830",
                                        "profileid": "600498",
                                        "r": "0",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "0",
                                        "status": "b Starc",
                                        "dismissal_fielders": null
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
}

}

# Function to replace `None` (JSON null) values with a default value
def replace_null_with_default(json_str, default_value="Unknown"):
    # Load JSON data
    data = json.loads(json_str)
    
    # Function to recursively replace `None` values with the default value
    def recursive_replace(obj):
        if isinstance(obj, dict):
            return {key: recursive_replace(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [recursive_replace(item) for item in obj]
        elif obj is None:
            return default_value
        return obj
    
    # Replace `None` values with default value in the entire data structure
    return recursive_replace(data)

# Call the function with the JSON data and print the result
updated_data = replace_null_with_default(json_data, "Unknown")

# Print the updated data
print(json.dumps(updated_data, indent=4))
