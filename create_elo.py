import pandas as pd
import math

DEFAULT_RATING = 1000
FACTOR = 461.3357857391371
K = 49
FLOOR = 0.5908222952865976
WIN_RATE_FLOOR = 0.19767074850012234
CEIL = 1.398889540374118

def expected_win(rating_a, rating_b, Factor):
    quotient_a = math.exp(rating_a / Factor)
    quotient_b = math.exp(rating_b / Factor)
    expected_a = quotient_a / (quotient_a + quotient_b)
    expected_b = quotient_b / (quotient_a + quotient_b)
    return expected_a, expected_b

def update_elo(rating, expected, actual, K):
    return rating + K * (actual - expected)

def process_matches(df, Factor, K):
    rating = {name: DEFAULT_RATING for name in df["Visitor"].unique()}
    rating_history = {name: [DEFAULT_RATING] for name in df["Visitor"].unique()}

    for match in df.itertuples(index=False):
        visitor, home, result = match[2], match[4], match[-1]
        rating_visitor, rating_home = rating[visitor], rating[home]
        
        expected_visitor, expected_home = expected_win(rating_visitor, rating_home, Factor)
        rating[visitor], rating[home] = (
            update_elo(rating_visitor, expected_visitor, 1 - result, K),
            update_elo(rating_home, expected_home, result, K)
        )
        
        rating_history[visitor].append(rating[visitor])
        rating_history[home].append(rating[home])
    
    return rating, rating_history

def test_matches(rating, df, Factor):
    test_result = []
    for match in df.itertuples(index=False):
        visitor, home, result = match[2], match[4], match[-1]
        expected_win_home = expected_win(rating[home], rating[visitor], Factor)[0]
        test_result.append(result - expected_win_home)
    return test_result

def add_game_odds(df, season):
    odds = pd.read_json(f"match_data_with_dates_{season}.json")
    odds_list = []
    for match in df.itertuples(index=False):
        date, visitor = match[0], match[2]
        odd = odds[(odds["Date"] == date) & (odds["Away Team"] == visitor)]
        if odd.empty:
            
            odds_list.append((None, None, None))
        else:
            odds_list.append((odd["Home Odds"].iloc[0], odd["Draw Odds"].iloc[0], odd["Away Odds"].iloc[0]))

    df = df.assign(HO=[odd[0] for odd in odds_list], DO=[odd[1] for odd in odds_list], AO=[odd[2] for odd in odds_list])
    return df

def pick_team(rating_home, rating_visitor, odds_home, odds_visitor, FLOOR, WIN_RATE_FLOOR, Factor):
    expected_home, expected_visitor = expected_win(rating_home, rating_visitor, Factor)
    return_home = expected_home * (odds_home - 1) - expected_visitor
    return_visitor = expected_visitor * (odds_visitor - 1) - expected_home
    flag_home = return_home > return_visitor
    flag_bet = (flag_home and expected_home > WIN_RATE_FLOOR) or (not flag_home and expected_visitor > WIN_RATE_FLOOR)
    return max(return_home, return_visitor), flag_home, flag_bet

def main(factor, k, floor, win_rate_floor, ceil, season):
    Factor, K, FLOOR, WIN_RATE_FLOOR, CEIL = factor, k, floor, win_rate_floor, ceil

    file_path = f"Database/{season}/{season}.csv"
    df = pd.read_csv(file_path)

    df["Res"] = (df["Gh"] - df["Gv"]).apply(lambda x: (1 + x / abs(x)) / 2)
    train_df, test_df = df.head(int(0.5 * len(df))), df.tail(int(0.5 * len(df)))

    rating, _ = process_matches(train_df, Factor, K)
    test_df = add_game_odds(test_df, season)

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

if __name__ == "__main__":
    #print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "18-19"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "19-20"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "20-21"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "21-22"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "22-23"))
    print(main(FACTOR, K, FLOOR, WIN_RATE_FLOOR, CEIL, "23-24"))