import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def main():
    YEAR = 2019
    stats = pd.read_csv(f"data/pitching-stats-{YEAR}.csv", index_col="player_id")
    stats.drop(index=stats[stats.ip == 0].index, inplace=True)
    stats["era"] = stats.er / stats.ip * 9
    stats["whip"] = (stats.bb + stats.h) / stats.ip
    stats["sv/hld"] = stats.sv + stats.hld
    stats.drop(columns=["er", "ip", "sv", "hld", "bb", "h"], inplace=True)

    max_stats = ["w", "so", "sv/hld"]
    min_stats = ["era", "whip"]

    # Just starters
    starters = stats[stats.SP]
    starters_stats = pd.DataFrame(
        MinMaxScaler().fit_transform(starters[max_stats]),
        index=starters.index,
        columns=max_stats,
    )
    starters_stats[min_stats] = 1 - MinMaxScaler().fit_transform(starters[min_stats])
    starters_stats["score"] = starters_stats.mean(axis=1)
    starters_final = pd.merge(
        stats.name_full,
        starters_stats,
        how="right",
        left_index=True,
        right_index=True,
    ).sort_values("score", ascending=False)
    starters_final.to_csv(f"rankings/{YEAR}/pitching-rankings-{YEAR}-SP.csv")

    # Just relievers
    releivers = stats[stats.RP]
    releivers_stats = pd.DataFrame(
        MinMaxScaler().fit_transform(releivers[max_stats]),
        index=releivers.index,
        columns=max_stats,
    )
    releivers_stats[min_stats] = 1 - MinMaxScaler().fit_transform(releivers[min_stats])
    releivers_stats["score"] = releivers_stats.mean(axis=1)
    relievers_final = pd.merge(
        stats.name_full,
        releivers_stats,
        how="right",
        left_index=True,
        right_index=True,
    ).sort_values("score", ascending=False)
    relievers_final.to_csv(f"rankings/{YEAR}/pitching-rankings-{YEAR}-RP.csv")

    # All pitchers
    pitchers_stats = pd.DataFrame(
        MinMaxScaler().fit_transform(stats[max_stats]),
        index=stats.index,
        columns=max_stats,
    )
    pitchers_stats[min_stats] = 1 - MinMaxScaler().fit_transform(stats[min_stats])
    pitchers_stats["score"] = pitchers_stats.mean(axis=1)
    pitchers_final = pd.merge(
        stats.name_full,
        pitchers_stats,
        how="right",
        left_index=True,
        right_index=True,
    ).sort_values("score", ascending=False)
    pitchers_final.to_csv(f"rankings/{YEAR}/pitching-rankings-{YEAR}.csv")


if __name__ == "__main__":
    main()
