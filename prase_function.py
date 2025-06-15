def parse_cricket_data(raw_data):
    # Helper function to convert string 'True'/'False' to boolean and handle None for null values
    def convert_to_boolean(value):
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
        return value

    def recursive_conversion(data):
        """Recursively convert string 'True'/'False' to boolean and 'None' to None."""
        if isinstance(data, dict):
            return {key: recursive_conversion(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [recursive_conversion(item) for item in data]
        else:
            return convert_to_boolean(data)

    # Apply recursive conversion to the entire raw data
    parsed_data = recursive_conversion(raw_data)
    
    # Extracting key match details
    match = parsed_data['scores']['category'][0]['match']
    
    match_info = {
        "match_id": match['id'],
        "status": match['status'],
        "venue": match['venue'],
        "date_range": match['date_range'],
        "home_team": match['home']['name'],
        "away_team": match['away']['name'],
        "home_score": match['home']['totalscore'],
        "away_score": match['away']['totalscore'],
        "toss_winner": match['comment']['toss_winner_teamid'],  # Adjust based on team name mapping
        "post_info": match['comment']['post']
    }

    # Organizing innings and player performance
    innings_data = []
    for inning in match['inning']:
        inning_info = {
            "inning_number": inning['inningnum'],
            "team": inning['name'],
            "total_runs": inning['total']['tot'],
            "wickets": inning['total']['wickets'],
            "batsmen": []
        }

        # Extracting batsman stats
        for batsman in inning['batsmanstats']['player']:
            batsman_info = {
                "name": batsman['batsman'],
                "runs": batsman['r'],
                "balls_faced": batsman['b'],
                "status": batsman['status']
            }
            inning_info["batsmen"].append(batsman_info)
        
        # Add inning information to innings_data
        innings_data.append(inning_info)
    
    # Organizing bowlers' performance
    bowlers_data = []
    for bowler in match['inning'][0]['bowlers']['player']:
        bowler_info = {
            "name": bowler['bowler'],
            "overs": bowler['o'],
            "runs_given": bowler['r'],
            "wickets_taken": bowler['w']
        }
        bowlers_data.append(bowler_info)
    
    # Organizing wickets data (who got out, how, and who bowled)
    wickets_data = []
    for wicket in match['wickets']['wicket']:
        wicket_info = {
            "inning": wicket['inning'],
            "player": wicket['player'],
            "wicket_details": wicket['post'],
            "runs_scored": wicket['runs']
        }
        wickets_data.append(wicket_info)
    
    # Building final parsed output
    parsed_output = {
        "match_info": match_info,
        "innings": innings_data,
        "bowlers": bowlers_data,
        "wickets": wickets_data
    }

    return parsed_output

if __name__ == "__main__":
    # Replace `raw_data` with the actual raw data dictionary provided
    raw_data = {
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
                                        "b": "56",
                                        "bat": "False",
                                        "batsman": "M Labuschagne",
                                        "dismissal_bowler": "696401",
                                        "dismissal_type": "caught",
                                        "dots": "",
                                        "id": "11385",
                                        "profileid": "787987",
                                        "r": "17",
                                        "s4": "1",
                                        "s6": "0",
                                        "sr": "30.35",
                                        "status": "c Verreynne b Jansen",
                                        "dismissal_fielders": {
                                            "dismissal_fielder": {
                                                "name": "K Verreynne",
                                                "profileid": "595004"
                                            }
                                        }
                                    },
                                    {
                                        "b": "3",
                                        "bat": "False",
                                        "batsman": "C Green",
                                        "dismissal_bowler": "550215",
                                        "dismissal_type": "caught",
                                        "dots": "",
                                        "id": "11159",
                                        "profileid": "1076713",
                                        "r": "4",
                                        "s4": "1",
                                        "s6": "0",
                                        "sr": "133.33",
                                        "status": "c Markram b Rabada",
                                        "dismissal_fielders": {
                                            "dismissal_fielder": {
                                                "name": "AK Markram",
                                                "profileid": "600498"
                                            }
                                        }
                                    },
                                    {
                                        "b": "112",
                                        "bat": "False",
                                        "batsman": "SPD Smith",
                                        "dismissal_bowler": "600498",
                                        "dismissal_type": "caught",
                                        "dots": "",
                                        "id": "2725",
                                        "profileid": "267192",
                                        "r": "66",
                                        "s4": "10",
                                        "s6": "0",
                                        "sr": "58.92",
                                        "status": "c Jansen b Markram",
                                        "dismissal_fielders": {
                                            "dismissal_fielder": {
                                                "name": "M Jansen",
                                                "profileid": "696401"
                                            }
                                        }
                                    },
                                    {
                                        "b": "13",
                                        "bat": "False",
                                        "batsman": "TM Head",
                                        "dismissal_bowler": "696401",
                                        "dismissal_type": "caught",
                                        "dots": "",
                                        "id": "6891",
                                        "profileid": "530011",
                                        "r": "11",
                                        "s4": "1",
                                        "s6": "0",
                                        "sr": "84.61",
                                        "status": "c Verreynne b Jansen",
                                        "dismissal_fielders": {
                                            "dismissal_fielder": {
                                                "name": "K Verreynne",
                                                "profileid": "595004"
                                            }
                                        }
                                    },
                                    {
                                        "b": "92",
                                        "bat": "False",
                                        "batsman": "BJ Webster",
                                        "dismissal_bowler": "550215",
                                        "dismissal_type": "caught",
                                        "dots": "",
                                        "id": "10943",
                                        "profileid": "381329",
                                        "r": "72",
                                        "s4": "11",
                                        "s6": "0",
                                        "sr": "78.26",
                                        "status": "c Bedingham b Rabada",
                                        "dismissal_fielders": {
                                            "dismissal_fielder": {
                                                "name": "DG Bedingham",
                                                "profileid": "498585"
                                            }
                                        }
                                    },
                                    {
                                        "b": "31",
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
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "6",
                                        "bat": "False",
                                        "batsman": "PJ Cummins",
                                        "dismissal_bowler": "550215",
                                        "dismissal_type": "bowled",
                                        "dots": "",
                                        "id": "5166",
                                        "profileid": "489889",
                                        "r": "1",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "16.66",
                                        "status": "b Rabada",
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "12",
                                        "bat": "False",
                                        "batsman": "MA Starc",
                                        "dismissal_bowler": "550215",
                                        "dismissal_type": "bowled",
                                        "dots": "",
                                        "id": "2929",
                                        "profileid": "311592",
                                        "r": "1",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "8.33",
                                        "status": "b Rabada",
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "4",
                                        "bat": "False",
                                        "batsman": "NM Lyon",
                                        "dismissal_bowler": "696401",
                                        "dismissal_type": "bowled",
                                        "dots": "",
                                        "id": "5095",
                                        "profileid": "272279",
                                        "r": "0",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "0",
                                        "status": "b Jansen",
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "1",
                                        "bat": "True",
                                        "batsman": "JR Hazlewood",
                                        "dismissal_bowler": "",
                                        "dismissal_type": "not out",
                                        "dots": "",
                                        "id": "6606",
                                        "profileid": "288284",
                                        "r": "0",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "0",
                                        "status": "not out",
                                        "dismissal_fielders": None
                                    }
                                ]
                            },
                            "total": {
                                "b": "0",
                                "ext": "17",
                                "lb": "7",
                                "nb": "10",
                                "p": "0",
                                "rr": "",
                                "tot": "212 ( 56.4 )",
                                "wd": "0",
                                "wickets": "10"
                            },
                            "bowlers": {
                                "player": [
                                    {
                                        "ball": "False",
                                        "bowler": "Kagiso Rabada",
                                        "dots": "76",
                                        "er": "3.25",
                                        "id": "10934",
                                        "m": "5",
                                        "nb": "1",
                                        "o": "15.4",
                                        "profileid": "550215",
                                        "r": "51",
                                        "w": "5",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "False",
                                        "bowler": "Marco Jansen",
                                        "dots": "63",
                                        "er": "3.5",
                                        "id": "21649",
                                        "m": "5",
                                        "nb": "2",
                                        "o": "14",
                                        "profileid": "696401",
                                        "r": "49",
                                        "w": "3",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "False",
                                        "bowler": "Lungi Ngidi",
                                        "dots": "31",
                                        "er": "5.62",
                                        "id": "16044",
                                        "m": "0",
                                        "nb": "2",
                                        "o": "8",
                                        "profileid": "542023",
                                        "r": "45",
                                        "w": "0",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "False",
                                        "bowler": "Wiaan Mulder",
                                        "dots": "51",
                                        "er": "3.27",
                                        "id": "15675",
                                        "m": "3",
                                        "nb": "5",
                                        "o": "11",
                                        "profileid": "698189",
                                        "r": "36",
                                        "w": "0",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "False",
                                        "bowler": "Keshav Maharaj",
                                        "dots": "21",
                                        "er": "3.16",
                                        "id": "3596",
                                        "m": "0",
                                        "nb": "0",
                                        "o": "6",
                                        "profileid": "267724",
                                        "r": "19",
                                        "w": "1",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "False",
                                        "bowler": "Aiden Markram",
                                        "dots": "9",
                                        "er": "2.5",
                                        "id": "10830",
                                        "m": "0",
                                        "nb": "0",
                                        "o": "2",
                                        "profileid": "600498",
                                        "r": "5",
                                        "w": "1",
                                        "wd": "0"
                                    }
                                ]
                            },
                            "partnerships": None
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
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "23",
                                        "bat": "False",
                                        "batsman": "RD Rickelton",
                                        "dismissal_bowler": "311592",
                                        "dismissal_type": "caught",
                                        "dots": "",
                                        "id": "15612",
                                        "profileid": "605661",
                                        "r": "16",
                                        "s4": "3",
                                        "s6": "0",
                                        "sr": "69.56",
                                        "status": "c Khawaja b Starc",
                                        "dismissal_fielders": {
                                            "dismissal_fielder": {
                                                "name": "UT Khawaja",
                                                "profileid": "215155"
                                            }
                                        }
                                    },
                                    {
                                        "b": "44",
                                        "bat": "False",
                                        "batsman": "PWA Mulder",
                                        "dismissal_bowler": "489889",
                                        "dismissal_type": "bowled",
                                        "dots": "",
                                        "id": "15675",
                                        "profileid": "698189",
                                        "r": "6",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "13.63",
                                        "status": "b Cummins",
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "37",
                                        "bat": "True",
                                        "batsman": "T Bavuma",
                                        "dismissal_bowler": "",
                                        "dismissal_type": "not out",
                                        "dots": "",
                                        "id": "3216",
                                        "profileid": "372116",
                                        "r": "3",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "8.1",
                                        "status": "not out",
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "13",
                                        "bat": "False",
                                        "batsman": "T Stubbs",
                                        "dismissal_bowler": "288284",
                                        "dismissal_type": "bowled",
                                        "dots": "",
                                        "id": "21612",
                                        "profileid": "595978",
                                        "r": "2",
                                        "s4": "0",
                                        "s6": "0",
                                        "sr": "15.38",
                                        "status": "b Hazlewood",
                                        "dismissal_fielders": None
                                    },
                                    {
                                        "b": "9",
                                        "bat": "True",
                                        "batsman": "DG Bedingham",
                                        "dismissal_bowler": "",
                                        "dismissal_type": "not out",
                                        "dots": "",
                                        "id": "8376",
                                        "profileid": "498585",
                                        "r": "8",
                                        "s4": "2",
                                        "s6": "0",
                                        "sr": "88.88",
                                        "status": "not out",
                                        "dismissal_fielders": None
                                    }
                                ]
                            },
                            "total": {
                                "b": "0",
                                "ext": "8",
                                "lb": "8",
                                "nb": "0",
                                "p": "0",
                                "rr": "",
                                "tot": "43 ( 22 )",
                                "wd": "0",
                                "wickets": "4"
                            },
                            "bowlers": {
                                "player": [
                                    {
                                        "ball": "False",
                                        "bowler": "Mitchell Starc",
                                        "dots": "38",
                                        "er": "1.42",
                                        "id": "2929",
                                        "m": "3",
                                        "nb": "0",
                                        "o": "7",
                                        "profileid": "311592",
                                        "r": "10",
                                        "w": "2",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "False",
                                        "bowler": "Josh Hazlewood",
                                        "dots": "36",
                                        "er": "1.42",
                                        "id": "6606",
                                        "m": "3",
                                        "nb": "0",
                                        "o": "7",
                                        "profileid": "288284",
                                        "r": "10",
                                        "w": "1",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "True",
                                        "bowler": "Pat Cummins",
                                        "dots": "36",
                                        "er": "2",
                                        "id": "5166",
                                        "m": "3",
                                        "nb": "0",
                                        "o": "7",
                                        "profileid": "489889",
                                        "r": "14",
                                        "w": "1",
                                        "wd": "0"
                                    },
                                    {
                                        "ball": "False",
                                        "bowler": "Nathan Lyon",
                                        "dots": "5",
                                        "er": "1",
                                        "id": "5095",
                                        "m": "0",
                                        "nb": "0",
                                        "o": "1",
                                        "profileid": "272279",
                                        "r": "1",
                                        "w": "0",
                                        "wd": "0"
                                    }
                                ]
                            },
                            "partnerships": None
                        }
                    ],
                    "commentaries": {
                        "commentary": [
                            {
                                "balls": "6",
                                "batsman_id": "64531",
                                "bowler_id": "64244",
                                "byes": "0",
                                "id": "49892598",
                                "isfour": "True",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "21.6",
                                "over_ended": "True",
                                "post": "Cummins to Bedingham",
                                "runs": "4",
                                "wides": "0"
                            },
                            {
                                "balls": "5",
                                "batsman_id": "64531",
                                "bowler_id": "64244",
                                "byes": "0",
                                "id": "49892596",
                                "isfour": "True",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "21.5",
                                "over_ended": "False",
                                "post": "Cummins to Bedingham",
                                "runs": "4",
                                "wides": "0"
                            },
                            {
                                "balls": "4",
                                "batsman_id": "64531",
                                "bowler_id": "64244",
                                "byes": "0",
                                "id": "49892594",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "21.4",
                                "over_ended": "False",
                                "post": "Cummins to Bedingham",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "3",
                                "batsman_id": "64531",
                                "bowler_id": "64244",
                                "byes": "0",
                                "id": "49892592",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "21.3",
                                "over_ended": "False",
                                "post": "Cummins to Bedingham",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "2",
                                "batsman_id": "64531",
                                "bowler_id": "64244",
                                "byes": "0",
                                "id": "49892590",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "21.2",
                                "over_ended": "False",
                                "post": "Cummins to Bedingham",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "1",
                                "batsman_id": "58190",
                                "bowler_id": "64244",
                                "byes": "0",
                                "id": "49892587",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "21.1",
                                "over_ended": "False",
                                "post": "Cummins to Bavuma",
                                "runs": "1",
                                "wides": "0"
                            },
                            {
                                "balls": "6",
                                "batsman_id": "64531",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892585",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "20.6",
                                "over_ended": "True",
                                "post": "Hazlewood to Bedingham",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "5",
                                "batsman_id": "64531",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892583",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "20.5",
                                "over_ended": "False",
                                "post": "Hazlewood to Bedingham",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "4",
                                "batsman_id": "64531",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892581",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "20.4",
                                "over_ended": "False",
                                "post": "Hazlewood to Bedingham",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "3",
                                "batsman_id": "64531",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892580",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "4",
                                "noballs": "0",
                                "over": "20.3",
                                "over_ended": "False",
                                "post": "Hazlewood to Bedingham",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "2",
                                "batsman_id": "69697",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892576",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "True",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "20.2",
                                "over_ended": "False",
                                "post": "Hazlewood to Stubbs",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "1",
                                "batsman_id": "69697",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892575",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "20.1",
                                "over_ended": "False",
                                "post": "Hazlewood to Stubbs",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "6",
                                "batsman_id": "58190",
                                "bowler_id": "50724",
                                "byes": "0",
                                "id": "49892573",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "19.6",
                                "over_ended": "True",
                                "post": "Lyon to Bavuma",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "5",
                                "batsman_id": "58190",
                                "bowler_id": "50724",
                                "byes": "0",
                                "id": "49892572",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "19.5",
                                "over_ended": "False",
                                "post": "Lyon to Bavuma",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "4",
                                "batsman_id": "58190",
                                "bowler_id": "50724",
                                "byes": "0",
                                "id": "49892571",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "19.4",
                                "over_ended": "False",
                                "post": "Lyon to Bavuma",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "3",
                                "batsman_id": "58190",
                                "bowler_id": "50724",
                                "byes": "0",
                                "id": "49892570",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "19.3",
                                "over_ended": "False",
                                "post": "Lyon to Bavuma",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "2",
                                "batsman_id": "58190",
                                "bowler_id": "50724",
                                "byes": "0",
                                "id": "49892569",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "19.2",
                                "over_ended": "False",
                                "post": "Lyon to Bavuma",
                                "runs": "0",
                                "wides": "0"
                            },
                            {
                                "balls": "1",
                                "batsman_id": "69697",
                                "bowler_id": "50724",
                                "byes": "0",
                                "id": "49892567",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "19.1",
                                "over_ended": "False",
                                "post": "Lyon to Stubbs",
                                "runs": "1",
                                "wides": "0"
                            },
                            {
                                "balls": "6",
                                "batsman_id": "58190",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892565",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "18.6",
                                "over_ended": "True",
                                "post": "Hazlewood to Bavuma",
                                "runs": "2",
                                "wides": "0"
                            },
                            {
                                "balls": "5",
                                "batsman_id": "58190",
                                "bowler_id": "51367",
                                "byes": "0",
                                "id": "49892563",
                                "isfour": "False",
                                "issix": "False",
                                "iswicket": "False",
                                "legbyes": "0",
                                "noballs": "0",
                                "over": "18.5",
                                "over_ended": "False",
                                "post": "Hazlewood to Bavuma",
                                "runs": "0",
                                "wides": "0"
                            }
                        ]
                    },
                    "wickets": {
                        "wicket": [
                            {
                                "id": "1",
                                "inning": "1",
                                "overs": "6.3",
                                "player": "UT Khawaja",
                                "playerdid": "215155",
                                "post": "Usman Khawaja c Bedingham b Rabada 0 (20b 0x4 0x6 30m) SR: 0",
                                "runs": "12",
                                "wickets": "1"
                            },
                            {
                                "id": "2",
                                "inning": "1",
                                "overs": "17.6",
                                "player": "M Labuschagne",
                                "playerdid": "787987",
                                "post": "Marnus Labuschagne c ?Verreynne b Jansen 17 (56b 1x4 0x6 87m) SR: 30.35",
                                "runs": "46",
                                "wickets": "3"
                            },
                            {
                                "id": "3",
                                "inning": "1",
                                "overs": "6.6",
                                "player": "C Green",
                                "playerdid": "1076713",
                                "post": "Cameron Green c Markram b Rabada 4 (3b 1x4 0x6 2m) SR: 133.33",
                                "runs": "16",
                                "wickets": "2"
                            },
                            {
                                "id": "4",
                                "inning": "1",
                                "overs": "41.6",
                                "player": "SPD Smith",
                                "playerdid": "267192",
                                "post": "Steven Smith c Jansen b Markram 66 (112b 10x4 0x6 162m) SR: 58.92",
                                "runs": "146",
                                "wickets": "5"
                            },
                            {
                                "id": "5",
                                "inning": "1",
                                "overs": "23.2",
                                "player": "TM Head",
                                "playerdid": "530011",
                                "post": "Travis Head c ?Verreynne b Jansen 11 (13b 1x4 0x6 27m) SR: 84.61",
                                "runs": "67",
                                "wickets": "4"
                            },
                            {
                                "id": "6",
                                "inning": "1",
                                "overs": "54.4",
                                "player": "BJ Webster",
                                "playerdid": "381329",
                                "post": "Beau Webster c Bedingham b Rabada 72 (92b 11x4 0x6 139m) SR: 78.26",
                                "runs": "210",
                                "wickets": "8"
                            },
                            {
                                "id": "7",
                                "inning": "1",
                                "overs": "51.1",
                                "player": "AT Carey",
                                "playerdid": "326434",
                                "post": "Alex Carey b Maharaj 23 (31b 4x4 0x6 42m) SR: 74.19",
                                "runs": "192",
                                "wickets": "6"
                            },
                            {
                                "id": "8",
                                "inning": "1",
                                "overs": "52.4",
                                "player": "PJ Cummins",
                                "playerdid": "489889",
                                "post": "Pat Cummins b Rabada 1 (6b 0x4 0x6 5m) SR: 16.66",
                                "runs": "199",
                                "wickets": "7"
                            },
                            {
                                "id": "9",
                                "inning": "1",
                                "overs": "56.4",
                                "player": "MA Starc",
                                "playerdid": "311592",
                                "post": "Mitchell Starc b Rabada 1 (12b 0x4 0x6 19m) SR: 8.33",
                                "runs": "212",
                                "wickets": "10"
                            },
                            {
                                "id": "10",
                                "inning": "1",
                                "overs": "55.5",
                                "player": "NM Lyon",
                                "playerdid": "272279",
                                "post": "Nathan Lyon b Jansen 0 (4b 0x4 0x6 5m) SR: 0",
                                "runs": "211",
                                "wickets": "9"
                            },
                            {
                                "id": "1",
                                "inning": "2",
                                "overs": "0.6",
                                "player": "AK Markram",
                                "playerdid": "600498",
                                "post": "Aiden Markram b Starc 0 (6b 0x4 0x6) SR: 0",
                                "runs": "0",
                                "wickets": "1"
                            },
                            {
                                "id": "2",
                                "inning": "2",
                                "overs": "8.4",
                                "player": "RD Rickelton",
                                "playerdid": "605661",
                                "post": "Ryan Rickelton c Khawaja b Starc 16 (23b 3x4 0x6) SR: 69.56",
                                "runs": "19",
                                "wickets": "2"
                            },
                            {
                                "id": "3",
                                "inning": "2",
                                "overs": "15.2",
                                "player": "PWA Mulder",
                                "playerdid": "698189",
                                "post": "Wiaan Mulder b Cummins 6 (44b 0x4 0x6) SR: 13.63",
                                "runs": "25",
                                "wickets": "3"
                            },
                            {
                                "id": "4",
                                "inning": "2",
                                "overs": "20.2",
                                "player": "T Stubbs",
                                "playerdid": "595978",
                                "post": "Tristan Stubbs b Hazlewood 2 (13b 0x4 0x6) SR: 15.38",
                                "runs": "30",
                                "wickets": "4"
                            }
                        ]
                    },
                    "lineups": {
                        "home": {
                            "player": [
                                {
                                    "c": "1",
                                    "is_impact": "False",
                                    "name": "UT Khawaja",
                                    "profileid": "215155",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "M Labuschagne",
                                    "profileid": "787987",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "C Green",
                                    "profileid": "1076713",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "SPD Smith",
                                    "profileid": "267192",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "TM Head",
                                    "profileid": "530011",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "BJ Webster",
                                    "profileid": "381329",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "AT Carey",
                                    "profileid": "326434",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "PJ Cummins",
                                    "profileid": "489889",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "MA Starc",
                                    "profileid": "311592",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "NM Lyon",
                                    "profileid": "272279",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "JR Hazlewood",
                                    "profileid": "288284",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                }
                            ]
                        },
                        "away": {
                            "player": [
                                {
                                    "c": "1",
                                    "is_impact": "False",
                                    "name": "AK Markram",
                                    "profileid": "600498",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "RD Rickelton",
                                    "profileid": "605661",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "PWA Mulder",
                                    "profileid": "698189",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "T Bavuma",
                                    "profileid": "372116",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "T Stubbs",
                                    "profileid": "595978",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "2",
                                    "is_impact": "False",
                                    "name": "DG Bedingham",
                                    "profileid": "498585",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "2",
                                    "is_impact": "False",
                                    "name": "K Verreynne",
                                    "profileid": "595004",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "1",
                                    "is_impact": "False",
                                    "name": "M Jansen",
                                    "profileid": "696401",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "KA Maharaj",
                                    "profileid": "267724",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "K Rabada",
                                    "profileid": "550215",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                },
                                {
                                    "c": "0",
                                    "is_impact": "False",
                                    "name": "L Ngidi",
                                    "profileid": "542023",
                                    "ro": "0",
                                    "st": "0",
                                    "wickets": "",
                                    "wides": ""
                                }
                            ]
                        }
                    },
                    "matchinfo": {
                        "info": [
                            {
                                "name": "Toss",
                                "value": "South Africa, elected to bowl first"
                            },
                            {
                                "id": "",
                                "name": "Man Of Match",
                                "value": ""
                            },
                            {
                                "name": "Referee",
                                "value": ""
                            }
                        ]
                    },
                    "replacements": {
                        "home": None,
                        "away": None
                    }
                }
            }
        ]
    }
    }

    
    parsed_data = parse_cricket_data(raw_data)

    # Output parsed data
    print(parsed_data)