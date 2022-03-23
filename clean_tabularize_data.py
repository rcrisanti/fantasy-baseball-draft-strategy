from decimal import Decimal
import numpy as np
import pandas as pd


def convert_ip(ip) -> float:
    d = Decimal(ip).as_tuple()
    if d.exponent == 0 or d.digits[d.exponent] == 0:
        return float(ip)
    elif d.digits[d.exponent] == 1:
        return float(Decimal((d.sign, d.digits[: d.exponent], 0))) + 1 / 3
    elif d.digits[d.exponent] == 2:
        return float(Decimal((d.sign, d.digits[: d.exponent], 0))) + 2 / 3
    else:
        raise ValueError(f"unknown # IP {ip}")


def main():
    SEASON = 2021

    hitting_stats = pd.read_json(f"data/hitting-stats-{SEASON}.json")
    pitching_stats = pd.read_json(f"data/pitching-stats-{SEASON}.json")

    # Clean hitting stats
    hitting_stats.dropna(
        how="all", subset=["ab", "r", "h", "rbi", "hr", "sb"], inplace=True
    )
    hitting_stats.drop(columns=["team_id"], inplace=True)
    hitting_stats_clean = pd.merge(
        hitting_stats.loc[
            :, ["player_id", "name_full", "primary_position"]
        ].drop_duplicates(),
        hitting_stats.loc[:, ["player_id", "ab", "r", "h", "rbi", "hr", "sb"]]
        .groupby("player_id")
        .sum(),
        how="right",
        on="player_id",
    ).astype({"ab": int, "r": int, "h": int, "rbi": int, "hr": int, "sb": int})
    assert (
        hitting_stats_clean.shape[0]
        == np.unique(hitting_stats_clean.player_id).shape[0]
    ), "duplicate player IDs"

    # Clean pitching stats
    pitching_stats.dropna(
        how="all", subset=["w", "sv", "hld", "so", "er", "bb", "h", "ip"], inplace=True
    )
    pitching_stats.drop(columns=["team_id"], inplace=True)
    pitching_stats["ip"] = pitching_stats.ip.apply(convert_ip)
    pitching_stats_clean = pd.merge(
        pitching_stats.loc[
            :, ["player_id", "name_full", "primary_position"]
        ].drop_duplicates(),
        pitching_stats.loc[
            :, ["player_id", "w", "sv", "hld", "so", "er", "bb", "h", "ip"]
        ]
        .groupby("player_id")
        .sum(),
        how="right",
        on="player_id",
    ).astype(
        {"w": int, "hld": int, "sv": int, "bb": int, "h": int, "so": int, "er": int}
    )
    assert (
        pitching_stats_clean.shape[0] == np.unique(pitching_stats.player_id).shape[0]
    ), "duplicate player IDs"

    hitting_stats_clean.to_csv(f"data/hitting-stats-{SEASON}.csv", index=False)
    pitching_stats_clean.to_csv(f"data/pitching-stats-{SEASON}.csv", index=False)


if __name__ == "__main__":
    main()
