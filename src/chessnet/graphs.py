from typing import Literal

import pandas as pd
import igraph as ig

from chessnet.utils import ARTIFACTS_DIR


def csv_to_edgelist(
    database: str, directed: bool = False, drop_missing_elo: bool = True
) -> None:
    df = pd.read_csv(ARTIFACTS_DIR / (database + ".csv"))
    cols_to_dropna = ["White", "Black"]
    if drop_missing_elo:
        cols_to_dropna += ["WhiteElo", "BlackElo"]
    df = df[cols_to_dropna].dropna()
    edges = df[["White", "Black"]].drop_duplicates()
    g = ig.Graph.DataFrame(edges)
    if not directed:
        g = g.as_undirected()
    g = g.simplify()
    g.vs.select(_degree=0).delete()  # Remove isolates
    name = database + ("_directed" if directed else "_undirected") + ".edgelist"
    g.write_edgelist(str(ARTIFACTS_DIR / name))


def read_edgelist(database: str, directed: bool = False) -> ig.Graph:
    name = database + ("_directed" if directed else "_undirected") + ".edgelist"
    filename = str(ARTIFACTS_DIR / name)
    g = ig.Graph.Read_Edgelist(filename, directed=directed)
    return g


def read_randomized_edgelist(
    database: str, mode: Literal["fabien-viger"] = "fabien-viger"
) -> ig.Graph:
    name = f"{database}_randomized_{mode}.edgelist"
    filename = str(ARTIFACTS_DIR / name)
    g = ig.Graph.Read_Edgelist(filename, directed=False)
    return g


def create_randomized_graph(
    database: str, mode: Literal["fabien-viger"] = "fabien-viger"
) -> None:
    g = read_edgelist(database, directed=False)
    if mode == "fabien-viger":
        g = ig.Graph.Degree_Sequence(g.degree(), method="vl")
    g = g.simplify()
    g.vs.select(_degree=0).delete()  # Remove isolates
    name = f"{database}_randomized_{mode}.edgelist"
    g.write_edgelist(str(ARTIFACTS_DIR / name))


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--parse-portal", action="store_true")
    parser.add_argument("--parse-otb", action="store_true")
    parser.add_argument("--directed", action="store_true")
    parser.add_argument("--randomize-portal", action="store_true")
    parser.add_argument("--randomize-otb", action="store_true")
    args = parser.parse_args()

    if args.parse_otb:
        csv_to_edgelist("OM_OTB_201609", directed=args.directed)

    if args.parse_portal:
        csv_to_edgelist("OM_Portal_201510", directed=args.directed)

    if args.randomize_otb:
        create_randomized_graph("OM_OTB_201609", mode="fabien-viger")

    if args.randomize_portal:
        create_randomized_graph("OM_Portal_201510", mode="fabien-viger")
