import pandas as pd


def convert_outfield(pos):
    if pos == "D":
        return pos

    if pos == "O" or int(pos) in range(7, 10):
        return "OF"
    else:
        return pos


def main():
    stats = pd.read_csv("data/hitting-stats-2021.csv", index_col="player_id")
    stats["primary_position"] = stats.primary_position.apply(convert_outfield)
    stats["ba"] = stats.h / stats.ab
    stats.drop(columns=["h", "ab"], inplace=True)

    for pos, pos_players in stats.groupby("primary_position"):
        normed_stats = (
            pos_players.drop(columns=["name_full", "primary_position"])
            / pos_players.drop(columns=["name_full", "primary_position"]).max()
        )
        normed_stats["score"] = normed_stats.mean(axis=1)
        final = pd.merge(
            pos_players["name_full"],
            normed_stats,
            how="right",
            left_index=True,
            right_index=True,
        ).sort_values("score", ascending=False)
        final.to_csv(f"rankings/hitting-ranksings-2021-pos-{pos}.csv")

    # Do one for all players
    normed_stats = (
        stats.drop(columns=["name_full", "primary_position"])
        / stats.drop(columns=["name_full", "primary_position"]).max()
    )
    normed_stats["score"] = normed_stats.mean(axis=1)
    final = pd.merge(
        stats[["name_full", "primary_position"]],
        normed_stats,
        how="right",
        left_index=True,
        right_index=True,
    ).sort_values("score", ascending=False)
    final.to_csv(f"rankings/hitting-ranksings-2021.csv")


if __name__ == "__main__":
    main()
