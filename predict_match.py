from create_elo import *

# ELO constants
DEFAULT_RATING = 1000
FACTOR = 461.3357857391371
K = 49
FLOOR = 0.5908222952865976
WIN_RATE_FLOOR = 0.19767074850012234
CEIL = 1.398889540374118


home_name = "Colorado Avalanche"
away_name = "Vegas Golden Knights"
odds_home = 2.18
odds_visitor = 2.88
season = "23-24"

    # Load and preprocess match data
file_path = f"Database/{season}/{season}.csv"
df = pd.read_csv(file_path)
df["Res"] = (df["Gh"] - df["Gv"]).apply(lambda x: (1 + x / abs(x)) / 2)

rating, _ = process_matches(df, FACTOR, K)

expected_return, home_pick, should_bet = pick_team(rating[home_name], rating[away_name], odds_home, odds_visitor, FLOOR, WIN_RATE_FLOOR, FACTOR)

if should_bet:
    if home_pick:
        print(f"You should bet on {home_name}, for an expected return of: {expected_return}")
    if not home_pick:
        print(f"You should bet on {away_name}, for an expected return of: {expected_return}")
else:
    print("You should not bet as the expected return is too low. ")
