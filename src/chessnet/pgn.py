from collections import defaultdict
from pathlib import Path
from typing import Union, List

from chess.pgn import read_headers
import pandas as pd

from chessnet.utils import ARTIFACTS_DIR, DATA_DIR


def pgn_to_dataframe(
    pgn_filename: Union[Path, str], fields: List[str], verbose: bool = False
) -> pd.DataFrame:

    file = open(pgn_filename, "r")

    data = defaultdict(list)

    i = 0
    pgn = read_headers(file)
    while pgn is not None:
        if verbose and i % 100000 == 0:
            print(f"Parsed {i} lines")
        i += 1
        for field in fields:
            value = pgn[field] if field in pgn else None
            data[field].append(value)
        try:
            pgn = read_headers(file)
        except UnicodeDecodeError:
            if verbose:
                print("Unidecode error:", i)
                print(pgn)
            pass
    return pd.DataFrame(data)


def pgn_to_csv(
    pgn_filename: Union[Path, str], fields: List[str], verbose: bool = False
) -> None:

    name = Path(pgn_filename).stem
    df = pgn_to_dataframe(pgn_filename, fields, verbose=verbose)
    df.to_csv(ARTIFACTS_DIR / (name + ".csv"))


def parse_om_otb():
    fields = [
        "White",
        "Black",
        "WhiteElo",
        "BlackElo",
        "Result",
        "ECO",
        "PlyCount",
        "Date",
    ]

    pgn_filename = DATA_DIR / "om_datasets" / "OM_OTB_201609.pgn"
    pgn_to_csv(pgn_filename, fields, verbose=True)


def parse_om_portal():
    fields = [
        "White",
        "Black",
        "WhiteElo",
        "BlackElo",
        "Result",
        "ECO",
        "PlyCount",
        "Date",
        "Site",
    ]

    pgn_filename = DATA_DIR / "om_datasets" / "OM_Portal_201510.pgn"
    pgn_to_csv(pgn_filename, fields, verbose=True)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--parse-portal", action="store_true")
    parser.add_argument("--parse-otb", action="store_true")
    args = parser.parse_args()

    if args.parse_otb:
        parse_om_otb()

    if args.parse_portal:
        parse_om_portal()
