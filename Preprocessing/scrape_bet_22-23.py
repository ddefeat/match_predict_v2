import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Load the HTML content
with open('Database/22-23/22-23.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

# List to hold match details
matches = []

# Initialize date variable to capture the date for each match
current_date = None

# Find all rows with the match details
match_rows = soup.find_all("tr")

for row in match_rows:
    # Check if the row contains a date
    date_cell = row.find("td", class_="l2 borbt borl")
    if date_cell:
        raw_date_text = date_cell.find("b").text.strip()
        # Parse and format date to YYYY-MM-DD
        current_date = datetime.strptime(raw_date_text, "%d %B %Y").strftime("%Y-%m-%d")

    # Ensure it has the correct structure with 'l2 match' class and odds columns
    match_info = row.find("td", class_="l2 match")
    if match_info and current_date:
        # Extract the time
        time = match_info.find("span", class_="time").text.strip()
        
        # Adjust the date if the time is between 00:00 and 12:00
        match_time = datetime.strptime(time, "%H:%M")
        if match_time.hour < 12:
            adjusted_date = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            adjusted_date = current_date

        # Extract the teams and replace "NY" with "New York"
        teams_text = match_info.find("a").text.strip()
        home_team, away_team = [team.strip() for team in teams_text.split(" - ")]
        
        if "NY " in home_team:
            home_team = home_team.replace("NY ", "New York ")
        if "NY " in away_team:
            away_team = away_team.replace("NY ", "New York ")

        # Find odds columns
        odds_columns = row.find_all("td", class_="r")
        if len(odds_columns) >= 3:
            home_odds = odds_columns[0].find("b").text.strip()
            draw_odds = odds_columns[1].find("b").text.strip()
            away_odds = odds_columns[2].find("b").text.strip()

            # Append the data
            matches.append({
                "Date": adjusted_date,
                "Time": time,
                "Home Team": home_team,
                "Away Team": away_team,
                "Home Odds": float(home_odds)*0.9,
                "Draw Odds": float(draw_odds)*0.9,
                "Away Odds": float(away_odds)*0.9
            })

# Define the output JSON file path
output_file = 'match_data_with_dates_22-23.json'

# Write the data to a JSON file
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(matches, json_file, ensure_ascii=False, indent=4)

print(f"Data has been written to {output_file}")