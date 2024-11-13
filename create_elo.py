import pandas as pd
import math

# Constants for ELO calculation
DEFAULT_RATING = 1000
FACTOR = 461.3357857391371
K = 49
FLOOR = 0.5908222952865976
WIN_RATE_FLOOR = 0.19767074850012234
CEIL = 1.398889540374118

def expected_win(rating_a, rating_b, Factor):
    """
    Calculate the expected win probability for two teams based on their ELO ratings.

    Parameters:
    rating_a (float): ELO rating of team A.
    rating_b (float): ELO rating of team B.
    Factor (float): Scaling factor for ELO calculations.

    Returns:
    tuple: Expected win probabilities for team A and team B.
    """
    quotient_a = math.exp(rating_a / Factor)
    quotient_b = math.exp(rating_b / Factor)
    expected_a = quotient_a / (quotient_a + quotient_b)
    expected_b = quotient_b / (quotient_a + quotient_b)
    return expected_a, expected_b

def update_elo(rating, expected, actual, K):
    """
    Update the ELO rating for a team after a match.

    Parameters:
    rating (float): Current ELO rating of the team.
    expected (float): Expected win probability.
    actual (float): Actual outcome (1 for win, 0 for loss).
    K (float): K-factor to adjust the impact of the outcome.

    Returns:
    float: Updated ELO rating.
    """
    return rating + K * (actual - expected)

def process_matches(df, Factor, K):
    """
    Calculate ELO ratings for each team based on match results.

    Parameters:
    df (DataFrame): Dataframe containing match data.
    Factor (float): Scaling factor for ELO calculations.
    K (float): K-factor for ELO update.

    Returns:
    tuple: Dictionary of final ELO ratings for each team and a rating history.
    """
    # Initialize ratings and rating history for each team
    rating = {name: DEFAULT_RATING for name in df["Visitor"].unique()}
    rating_history = {name: [DEFAULT_RATING] for name in df["Visitor"].unique()}

    # Iterate over each match to update ELO ratings
    for match in df.itertuples(index=False):
        visitor, home, result = match[2], match[4], match[-1]
        rating_visitor, rating_home = rating[visitor], rating[home]
        
        # Calculate expected win probabilities
        expected_visitor, expected_home = expected_win(rating_visitor, rating_home, Factor)
        
        # Update ELO ratings based on match result
        rating[visitor], rating[home] = (
            update_elo(rating_visitor, expected_visitor, 1 - result, K),
            update_elo(rating_home, expected_home, result, K)
        )
        
        # Save updated ratings to history
        rating_history[visitor].append(rating[visitor])
        rating_history[home].append(rating[home])
    
    return rating, rating_history

def test_matches(rating, df, Factor):
    """
    Test the model by calculating the difference between actual and expected outcomes.

    Parameters:
    rating (dict): Dictionary of ELO ratings for each team.
    df (DataFrame): Dataframe containing test match data.
    Factor (float): Scaling factor for ELO calculations.

    Returns:
    list: List of results showing the difference between actual and expected outcomes.
    """
    test_result = []
    for match in df.itertuples(index=False):
        visitor, home, result = match[2], match[4], match[-1]
        expected_win_home = expected_win(rating[home], rating[visitor], Factor)[0]
        test_result.append(result - expected_win_home)
    return test_result

def add_game_odds(df, season):
    """
    Add game odds to the dataframe from an external file.

    Parameters:
    df (DataFrame): Dataframe containing match data.
    season (str): Season identifier for file lookup.

    Returns:
    DataFrame: Updated dataframe with odds columns.
    """
    # Load odds data from JSON file
    odds = pd.read_json(f"match_data_with_dates_{season}.json")
    odds_list = []
    for match in df.itertuples(index=False):
        date, visitor = match[0], match[2]
        odd = odds[(odds["Date"] == date) & (odds["Away Team"] == visitor)]
        if odd.empty:
            odds_list.append((None, None, None))
        else:
            odds_list.append((odd["Home Odds"].iloc[0], odd["Draw Odds"].iloc[0], odd["Away Odds"].iloc[0]))

    # Add new columns for home, draw, and away odds
    df = df.assign(HO=[odd[0] for odd in odds_list], DO=[odd[1] for odd in odds_list], AO=[odd[2] for odd in odds_list])
    return df

def pick_team(rating_home, rating_visitor, odds_home, odds_visitor, FLOOR, WIN_RATE_FLOOR, Factor):
    """
    Determine which team to bet on based on expected returns and win probabilities.

    Parameters:
    rating_home (float): ELO rating of home team.
    rating_visitor (float): ELO rating of visiting team.
    odds_home (float): Odds for the home team win.
    odds_visitor (float): Odds for the visitor team win.
    FLOOR (float): Minimum expected return to place a bet.
    WIN_RATE_FLOOR (float): Minimum win probability to place a bet.
    Factor (float): Scaling factor for ELO calculations.

    Returns:
    tuple: Expected return, selected team flag, and betting decision flag.
    """
    expected_home, expected_visitor = expected_win(rating_home, rating_visitor, Factor)
    #return_home = expected_home * (odds_home - 1) - expected_visitor
    return_home = expected_home * odds_home - 1

    #return_visitor = expected_visitor * (odds_visitor - 1) - expected_home
    return_visitor = expected_visitor * odds_visitor - 1
    flag_home = return_home > return_visitor
    flag_bet = (flag_home and expected_home > WIN_RATE_FLOOR) or (not flag_home and expected_visitor > WIN_RATE_FLOOR)
    return max(return_home, return_visitor), flag_home, flag_bet

def main(factor, k, floor, win_rate_floor, ceil, season):
    """
    Run the ELO model for a given season and parameters, simulating betting results.

    Parameters:
    factor (float): Scaling factor for ELO calculations.
    k (float): K-factor for ELO update.
    floor (float): Minimum expected return to place a bet.
    win_rate_floor (float): Minimum win probability to place a bet.
    ceil (float): Maximum acceptable expected return.
    season (str): Season identifier for file lookup.

    Returns:
    float: Final balance after simulated betting.
    """
    Factor, K, FLOOR, WIN_RATE_FLOOR, CEIL = factor, k, floor, win_rate_floor, ceil

    # Load and preprocess match data
    file_path = f"Database/{season}/{season}.csv"
    df = pd.read_csv(file_path)
    df["Res"] = (df["Gh"] - df["Gv"]).apply(lambda x: (1 + x / abs(x)) / 2)
    
    # Split data into training and testing sets
    train_df, test_df = df.head(int(0.5 * len(df))), df.tail(int(0.5 * len(df)))

    # Process training matches to calculate ratings
    rating, _ = process_matches(train_df, Factor, K)
    
    # Add game odds to test matches
    test_df = add_game_odds(test_df, season)

    # Simulate betting
    bal, bets_won, bets_lost = 10000, 0, 0
    for match in test_df.itertuples(index=False):
        pick = pick_team(rating[match[4]], rating[match[2]], match[-3], match[-1], FLOOR, WIN_RATE_FLOOR, Factor)
        if FLOOR < pick[0] < ceil and pick[2]:
            bet = bal * pick[0] / 20
            bal -= bet
            if (match[-4] == 1 and pick[1]) or (match[-4] == 0 and not pick[1]):
                bal += match[-3 if pick[1] else -1] * bet
                bets_won += 1
            else:
                bets_lost += 1
    return bal


    
# Running the model for multiple seasons
if __name__ == "__main__":
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "19-20"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "20-21"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "21-22"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "22-23"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "23-24"))
    
