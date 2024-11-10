import pandas as pd
import csv
import math
import matplotlib.pyplot as plt

DEFAULT_RATING = 1000
Factor = 480
K = 40

def expected_win(rating_a, rating_b):
    quotient_a = math.exp(rating_a / Factor)
    quotient_b = math.exp(rating_b / Factor)
    expected_a = quotient_a / (quotient_a + quotient_b)
    expected_b = quotient_b / (quotient_a + quotient_b)
    return (expected_a, expected_b)

def update_elo(rating, expected, actual):
    return rating + K * (actual - expected)

def proccess_match(rating_visitor, rating_home, result):
    (expected_visitor, expected_home) = expected_win(rating_visitor, rating_home)
    return (
        update_elo(rating_visitor, expected_visitor, 1 - result),
        update_elo(rating_home, expected_home, result)
    )

def process_matches(matches):
    # Initialize ELO system
    rating = dict()
    rating_history = dict()  # Dictionary to store each team's rating history
    
    # Initialize ratings and history for each team
    for name in df["Visitor"].unique():
        rating[name] = DEFAULT_RATING
        rating_history[name] = [DEFAULT_RATING]  # Start with the default rating

    # Process each match and update ratings
    for match in matches.itertuples(index=False):
        visitor = match[2]
        home = match[4]
        
        # Update ratings
        rating[visitor], rating[home] = proccess_match(
            rating[visitor],
            rating[home],
            match[-1]
        )
        
        # Store the updated ratings after each match
        rating_history[visitor].append(rating[visitor])
        rating_history[home].append(rating[home])
    
    return rating, rating_history

def test_matches(rating, matches):
    test_result = []
    for match in matches.itertuples(index=False):
        visitor = match[2]
        home = match[4]
        test_result.append(match[-1] - expected_win(rating[home], rating[visitor])[0])
    return test_result


def add_game_odds(matches):
    odds = pd.read_json("match_data_with_dates.json")
    odds_list = []
    for match in matches.itertuples(index=False):
        date = match[0]
        visitor = match[2]
        odd = odds[(odds["Date"] == date) & (odds["Away Team"] == visitor)]
        
        if odd.empty:
            print("FUCKFUCKFUCKFUCK")
            odds_list.append((None, None, None))  # Use None if odds not found
        else:
            # Use .iloc[0] to access the first row of the matching result
            odds_list.append((odd["Home Odds"].iloc[0], odd["Draw Odds"].iloc[0], odd["Away Odds"].iloc[0]))
    
    # Directly create new columns in `matches`
    matches = matches.assign(
        HO=[odd[0] for odd in odds_list],
        DO=[odd[1] for odd in odds_list],
        AO=[odd[2] for odd in odds_list]
    )

    return matches

            
def pick_team(rating_home,rating_visiting,odds_home,odds_visiting):
    home=False
    expected_home,expected_visiting=expected_win(rating_home,rating_visiting)
    expected_profit_home = (odds_home - 1) * expected_home - 1
    expected_profit_visiting = (odds_visiting - 1) * expected_visiting - 1
    if expected_profit_home > expected_profit_visiting:
        home=True
    return max(expected_profit_home, expected_profit_visiting), expected_profit_home, expected_profit_visiting, home

# Define the path to the CSV file
file_path = '/Users/hugohultqvist/Desktop/match_predict_v2/Database/21-22/21-22.csv'

df = pd.read_csv(file_path)

# Preprocessing
diff = df["Gh"] - df["Gv"]
res = diff / abs(diff)
res = (1 + res) / 2
df["Res"] = res

# Test-train split
n = df.shape[0]
train_df = df.head(math.floor(.85 * n))
test_df = df.tail(math.ceil(.15 * n))

# Training
rating, rating_history = process_matches(train_df)

# Testing
test_result = test_matches(rating, test_df)

# Evaluate the results
right_guesses = 0
wrong = 0
for result in test_result:
    if result > 0:
        if result > 0.5:
            right_guesses += 1
    elif result > -0.5:
        wrong += 1

print("Right guesses:", right_guesses)
print("Wrong:", wrong)

# Plotting the rating change over games played for each team
# plt.figure(figsize=(12, 8))
# for team, history in list(rating_history.items())[:2]:
#     plt.plot(history, label=team)

# plt.xlabel("Games Played")
# plt.ylabel("ELO Rating")
# plt.title("ELO Rating Change Over Games Played for Each Team")
# plt.legend(loc="best", fontsize="small", ncol=2)
# plt.show()

test_df = add_game_odds(test_df)

bal = 10000

all_pick=[]
for match in test_df.itertuples(index=False):
    pick = pick_team(rating[match[4]],rating[match[2]],match[-3],match[-1])
    
    if pick[0] > 0:
        bet = bal / 20
        print(f"Bet: {bet}, balance{bal}")
        bal -= bet
        
        if       pick[3] and match[-4]==1:
            bal += match[-3]*bet
            print(f"Just won SEK {match[-3]*bet-bet}! Current balance: {bal}")
        elif     pick[3] and match[-4]==0:
             print(f"FUCK! Lost {bet}! Current balance: {bal}")
             
        elif not pick[3] and match[-4]==1:
             print(f"FUCK! Lost {bet}! Current balance: {bal}")
        elif not pick[3] and match[-4]==0:
            bal += match[-1]*bet
            print(f"Just won SEK {match[-1]*bet-bet}! Current balance: {bal}")
           

print(bal)
