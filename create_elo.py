import pandas as pd
import math

# Constants for ELO calculation
DEFAULT_RATING = 1000
FACTOR = 348.52756272674264
K = 33
FLOOR = 0.4756190754648416
WIN_RATE_FLOOR = 0.2946325964931914
CEIL = 0.9506928437169432


def expected_win(rating_a, rating_b, factor):
    """
    Calculate the expected win probability for two teams based on their ELO ratings.
    """
    exp_a = math.exp(rating_a / factor)
    exp_b = math.exp(rating_b / factor)
    expected_a = exp_a / (exp_a + exp_b)
    expected_b = exp_b / (exp_a + exp_b)
    return expected_a, expected_b


def update_elo(rating, expected, actual, k_factor):
    """
    Update the ELO rating for a team after a match.
    """
    return rating + k_factor * (actual - expected)


def process_matches(df, factor, k_factor):
    """
    Calculate ELO ratings for each team based on match results.
    """
    # Initialize ratings and rating history for each team
    ratings = {team: DEFAULT_RATING for team in df["Visitor"].unique()}
    ratings_history = {team: [DEFAULT_RATING] for team in df["Visitor"].unique()}

    # Iterate over each match to update ELO ratings
    for match in df.itertuples(index=False):
        visitor, home, result = match.Visitor, match.Home, match.Res
        rating_visitor, rating_home = ratings[visitor], ratings[home]

        # Calculate expected win probabilities
        expected_visitor, expected_home = expected_win(rating_visitor, rating_home, factor)

        # Update ELO ratings based on match result
        ratings[visitor] = update_elo(rating_visitor, expected_visitor, 1 - result, k_factor)
        ratings[home] = update_elo(rating_home, expected_home, result, k_factor)

        # Save updated ratings to history
        ratings_history[visitor].append(ratings[visitor])
        ratings_history[home].append(ratings[home])

    return ratings, ratings_history


def test_matches(ratings, df, factor):
    """
    Test the model by calculating the difference between actual and expected outcomes.
    """
    test_results = []
    for match in df.itertuples(index=False):
        visitor, home, result = match.Visitor, match.Home, match.Res
        expected_home = expected_win(ratings[home], ratings[visitor], factor)[0]
        test_results.append(result - expected_home)
    return test_results


def add_game_odds(df, season):
    """
    Add game odds to the dataframe from an external file.
    """
    odds = pd.read_json(f"match_data_with_dates_{season}.json")
    odds_list = []

    for match in df.itertuples(index=False):
        date, visitor = match.Date, match.Visitor
        match_odds = odds[(odds["Date"] == date) & (odds["Away Team"] == visitor)]

        if match_odds.empty:
            odds_list.append((None, None, None))
        else:
            odds_list.append(
                (match_odds["Home Odds"].iloc[0], match_odds["Draw Odds"].iloc[0], match_odds["Away Odds"].iloc[0])
            )

    # Add new columns for home, draw, and away odds
    df = df.assign(
        HomeOdds=[odd[0] for odd in odds_list],
        DrawOdds=[odd[1] for odd in odds_list],
        AwayOdds=[odd[2] for odd in odds_list],
    )
    return df


def pick_team(rating_home, rating_visitor, odds_home, odds_visitor, floor, win_rate_floor, factor):
    """
    Determine which team to bet on based on expected returns and win probabilities.
    """
    expected_home, expected_visitor = expected_win(rating_home, rating_visitor, factor)
    return_home = expected_home * odds_home - 1
    return_visitor = expected_visitor * odds_visitor - 1

    flag_home = return_home > return_visitor
    flag_bet = (flag_home and expected_home > win_rate_floor) or (
        not flag_home and expected_visitor > win_rate_floor
    )

    return max(return_home, return_visitor), flag_home, flag_bet


def main(factor, k_factor, floor, win_rate_floor, ceil, season):
    """
    Run the ELO model for a given season and parameters, simulating betting results.
    """
    # Load and preprocess match data
    file_path = f"Database/{season}/{season}.csv"
    df = pd.read_csv(file_path)
    df["Res"] = (df["Gh"] - df["Gv"]).apply(lambda x: (1 + x / abs(x)) / 2)

    # Split data into training and testing sets
    train_df = df.head(int(0.9 * len(df)))
    test_df = df.tail(int(0.1 * len(df)))

    # Process training matches to calculate ratings
    ratings, _ = process_matches(train_df, factor, k_factor)

    # Add game odds to test matches
    test_df = add_game_odds(test_df, season)

    # Simulate betting
    balance = 100
    for match in test_df.itertuples(index=False):
        pick = pick_team(
            ratings[match.Home],
            ratings[match.Visitor],
            match.HomeOdds,
            match.AwayOdds,
            floor,
            win_rate_floor,
            factor,
        )
        if floor < pick[0] < ceil and pick[2]:
            bet = balance * pick[0] / 20
            balance -= bet
            if (match.Res == 1 and pick[1]) or (match.Res == 0 and not pick[1]):
                balance += match.HomeOdds * bet if pick[1] else match.AwayOdds * bet

    return balance


# Running the model for multiple seasons
if __name__ == "__main__":
    for season in ["19-20", "20-21", "21-22", "22-23", "23-24"]:
        print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, season))