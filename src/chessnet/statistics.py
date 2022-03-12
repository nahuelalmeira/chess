import pandas as pd

from chessnet.utils import ARTIFACTS_DIR


def get_players_elo(database: str) -> pd.DataFrame:
    df = pd.read_csv(ARTIFACTS_DIR / f"{database}.csv")
    players = pd.concat(
        [
            df[["White", "WhiteElo"]].rename(
                columns={"White": "Player", "WhiteElo": "Elo"}
            ),
            df[["Black", "BlackElo"]].rename(
                columns={"Black": "Player", "BlackElo": "Elo"}
            ),
        ],
        ignore_index=True,
    ).dropna()
    grouped = players.groupby(by="Player").agg(["mean", "std"]).dropna()
    grouped.columns = grouped.columns.droplevel()
    grouped = grouped.rename(columns={"mean": "MeanElo", "std": "StdElo"})
    return grouped


def write_elo_data(database: str) -> None:
    elo_data = get_players_elo(database)
    elo_data.to_csv(ARTIFACTS_DIR / f"{database}_elo_data.csv")


def read_elo_data(database: str) -> pd.DataFrame:
    return pd.read_csv(ARTIFACTS_DIR / f"{database}_elo_data.csv").set_index("Player")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--elo-otb", action="store_true")
    parser.add_argument("--elo-portal", action="store_true")
    args = parser.parse_args()

    if args.elo_otb:
        write_elo_data("OM_OTB_201609")

    if args.elo_portal:
        write_elo_data("OM_Portal_201510")
