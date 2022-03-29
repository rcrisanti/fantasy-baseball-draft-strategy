from typing import Dict, List, Optional, Union
from urllib.parse import urljoin
import json
import requests
from tqdm import tqdm

HOST = "http://lookup-service-prod.mlb.com"


def get_teams(
    season: Union[int, str],
    sport_code: Optional[str] = "'mlb'",
    all_star_sw: Optional[str] = "'N'",
    sort_order: Optional[str] = None,
) -> List[Dict[str, str]]:
    full_path = urljoin(HOST, "/json/named.team_all_season.bam")
    r = requests.get(
        full_path,
        params=dict(
            sport_code=sport_code,
            season=season,
            all_star_sw=all_star_sw,
            sort_order=sort_order,
        ),
    )
    return r.json()["team_all_season"]["queryResults"]["row"]


def get_roster(team_id: Union[int, str], **kwargs) -> List[Dict[str, str]]:
    full_path = urljoin(HOST, "/json/named.roster_40.bam")
    kwargs["team_id"] = team_id
    kwargs["roster_40.col_in"] = kwargs.pop("col_in", None)
    kwargs["roster_40.col_ex"] = kwargs.pop("col_ex", None)
    r = requests.get(full_path, params=kwargs)
    return r.json()["roster_40"]["queryResults"]["row"]


def get_season_hitting_stats(
    player_id: Union[int, str],
    season: Union[int, str],
    game_type: Optional[str] = "'R'",
    league_list_id: Optional[str] = "'mlb'",
    **kwargs,
):
    full_path = urljoin(HOST, "/json/named.sport_hitting_tm.bam")
    kwargs["sport_hitting_tm.col_in"] = kwargs.pop("col_in", None)
    kwargs["sport_hitting_tm.col_ex"] = kwargs.pop("col_ex", None)
    kwargs.update(
        dict(
            player_id=player_id,
            season=season,
            game_type=game_type,
            league_list_id=league_list_id,
        )
    )
    r = requests.get(full_path, params=kwargs)
    return r.json()["sport_hitting_tm"]["queryResults"].get("row", {})


def get_season_pitching_stats(
    player_id: Union[int, str],
    season: Union[int, str],
    game_type: Optional[str] = "'R'",
    league_list_id: Optional[str] = "'mlb'",
    **kwargs,
):
    full_path = urljoin(HOST, "/json/named.sport_pitching_tm.bam")
    kwargs["sport_pitching_tm.col_in"] = kwargs.pop("col_in", None)
    kwargs["sport_pitching_tm.col_ex"] = kwargs.pop("col_ex", None)
    kwargs.update(
        dict(
            player_id=player_id,
            season=season,
            game_type=game_type,
            league_list_id=league_list_id,
        )
    )
    r = requests.get(full_path, params=kwargs)
    return r.json()["sport_pitching_tm"]["queryResults"].get("row", {})


def main():
    SEASON = 2019
    teams = get_teams(SEASON)
    players = []
    for team in tqdm(teams):
        roster = get_roster(
            team["team_id"],
            col_in=[
                "name_full",
                "team_name",
                "team_id",
                "primary_position",
                "player_id",
            ],
        )
        players.extend(roster)

    hitting_stats = []
    pitching_stats = []
    for player in tqdm(players):
        try:
            position_code = int(player["primary_position"])
        except ValueError:
            # non numeric position codes ("O" = outfield, "D" = designated hitter)
            position_code = 10

        if position_code == 1:
            stats = get_season_pitching_stats(
                player["player_id"],
                season=SEASON,
                col_in=[
                    "w",
                    "sv",
                    "hld",
                    "so",
                    "er",
                    "bb",
                    "h",
                    "ip",
                    "g",
                    "gs",
                    "team_full",
                ],
            )
            if isinstance(stats, list):
                for team_stats in stats:
                    team_stats.update(player)
                    pitching_stats.append(team_stats)
            else:
                player.update(stats)
                pitching_stats.append(player)
        else:
            stats = get_season_hitting_stats(
                player["player_id"],
                season=SEASON,
                col_in=["r", "hr", "rbi", "h", "ab", "sb", "team_full"],
            )
            if isinstance(stats, list):
                for team_stats in stats:
                    team_stats.update(player)
                    hitting_stats.append(team_stats)
            else:
                player.update(stats)
                hitting_stats.append(player)

    with open(f"data/hitting-stats-{SEASON}.json", "w") as f:
        json.dump(hitting_stats, f)

    with open(f"data/pitching-stats-{SEASON}.json", "w") as f:
        json.dump(pitching_stats, f)


if __name__ == "__main__":
    main()
