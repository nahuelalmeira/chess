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
