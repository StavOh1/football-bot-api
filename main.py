
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "c14abe3cef46e8b6629237366829cd2f"
HEADERS = {"x-apisports-key": API_KEY}

def get_live_games():
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"live": "all"}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def get_team_live_status(team_name, live_data):
    for fixture in live_data["response"]:
        home = fixture["teams"]["home"]["name"]
        away = fixture["teams"]["away"]["name"]
        if team_name.lower() in (home.lower(), away.lower()):
            goals_home = fixture["goals"]["home"]
            goals_away = fixture["goals"]["away"]
            minute = fixture["fixture"]["status"].get("elapsed", "?")
            status = fixture["fixture"]["status"]["short"]
            return f"{home} נגד {away} | {goals_home}-{goals_away} | דקה {minute} | סטטוס: {status}"
    return "הקבוצה לא משחקת כרגע."

def get_team_events(team_name, live_data):
    for fixture in live_data["response"]:
        home = fixture["teams"]["home"]["name"]
        away = fixture["teams"]["away"]["name"]
        if team_name.lower() in (home.lower(), away.lower()):
            events = fixture.get("events", [])
            messages = []
            for event in events:
                team = event["team"]["name"]
                player = event["player"]["name"]
                event_type = event["type"]
                detail = event["detail"]
                minute = event["time"]["elapsed"]
                messages.append(f"דקה {minute}: {team} - {player} - {event_type}: {detail}")
            return "\n".join(messages) if messages else "אין אירועים זמינים כרגע."
    return "אין אירועים לקבוצה זו כרגע."

@app.route("/chat", methods=["POST"])
def chat_api():
    user_question = request.json.get("question", "")
    live_data = get_live_games()

    if "כרטיס" in user_question or "עבירה" in user_question or "אירוע" in user_question:
        for team in ["מכבי חיפה", "מכבי תל אביב", "הפועל באר שבע", "בית"ר ירושלים"]:
            if team in user_question:
                return jsonify({"answer": get_team_events(team, live_data)})
        return jsonify({"answer": "אנא צייני את שם הקבוצה לגבי האירוע."})

    elif "תוצאה" in user_question or "כמה" in user_question or "מה קורה עם" in user_question:
        for team in ["מכבי חיפה", "מכבי תל אביב", "בית"ר ירושלים", "הפועל באר שבע"]:
            if team in user_question:
                return jsonify({"answer": get_team_live_status(team, live_data)})
        return jsonify({"answer": "לא מצאתי קבוצה תואמת בשאלה."})

    elif "מי משחק" in user_question:
        games = []
        for fixture in live_data["response"]:
            home = fixture["teams"]["home"]["name"]
            away = fixture["teams"]["away"]["name"]
            games.append(f"{home} נגד {away}")
        return jsonify({"answer": "\n".join(games)})

    else:
        return jsonify({"answer": "מצטער, לא הבנתי את השאלה. נסי שוב."})

if __name__ == "__main__":
    app.run(debug=True)
