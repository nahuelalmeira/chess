from typing import Literal, Union
from black import InvalidInput

import pandas as pd
import igraph as ig
import networkx as nx

from chessnet.utils import ARTIFACTS_DIR


def get_players_degree(database: str) -> pd.DataFrame:
    g = csv_to_igraph(database, directed=False, drop_missing_elo=True)
    node_df = pd.DataFrame(
        {
            "Player": [v["name"] for v in g.vs()],
            "k": [v.degree() for v in g.vs()],
        }
    ).set_index("Player")
    return node_df


def csv_to_igraph(database: str, directed: bool = False, drop_missing_elo: bool = True):
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
    return g


def csv_to_edgelist(
    database: str, directed: bool = False, drop_missing_elo: bool = True
) -> None:
    g = csv_to_igraph(database, directed=directed, drop_missing_elo=drop_missing_elo)
    name = database + ("_directed" if directed else "_undirected") + ".edgelist"
    g.write_edgelist(str(ARTIFACTS_DIR / name))


def read_edgelist(
    database: str,
    directed: bool = False,
    package: Literal["igraph", "networkx"] = "igraph",
) -> Union[ig.Graph, nx.Graph]:
    name = database + ("_directed" if directed else "_undirected") + ".edgelist"
    filename = str(ARTIFACTS_DIR / name)
    if package == "igraph":
        return ig.Graph.Read_Edgelist(filename, directed=directed)
    elif package == "networkx":
        return nx.read_edgelist(
            filename, create_using=nx.DiGraph if directed else nx.Graph
        )
    else:
        raise InvalidInput("package must be in ['igraph', 'networkx']")


def read_randomized_edgelist(
    database: str, mode: Literal["fabien-viger"] = "fabien-viger"
) -> ig.Graph:
    name = f"{database}_randomized_{mode}.edgelist"
    filename = str(ARTIFACTS_DIR / name)
    g = ig.Graph.Read_Edgelist(filename, directed=False)
    return g


def read_rewired_edgelist(database: str, nswap_ecount_times: int = 10) -> ig.Graph:
    name = f"{database}_rewired_f{nswap_ecount_times}.edgelist"
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


def create_rewired_graph(database: str, nswap_ecount_times: int = 10):
    g = read_edgelist(database, directed=False, package="networkx")
    nswap = nswap_ecount_times * g.number_of_edges()
    max_tries = 10 * nswap
    h = nx.double_edge_swap(g, nswap=nswap, max_tries=max_tries)
    name = f"{database}_rewired_f{nswap_ecount_times}.edgelist"
    nx.write_edgelist(h, ARTIFACTS_DIR / name, data=False)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--parse-portal", action="store_true")
    parser.add_argument("--parse-otb", action="store_true")
    parser.add_argument("--directed", action="store_true")
    parser.add_argument("--randomize-portal", action="store_true")
    parser.add_argument("--randomize-otb", action="store_true")
    parser.add_argument("--rewire-portal", action="store_true")
    parser.add_argument("--rewire-otb", action="store_true")
    parser.add_argument("--nswap-frac", type=float, default=10)
    args = parser.parse_args()

    if args.parse_otb:
        csv_to_edgelist("OM_OTB_201609", directed=args.directed)

    if args.parse_portal:
        csv_to_edgelist("OM_Portal_201510", directed=args.directed)

    if args.randomize_otb:
        create_randomized_graph("OM_OTB_201609", mode="fabien-viger")

    if args.randomize_portal:
        create_randomized_graph("OM_Portal_201510", mode="fabien-viger")

    if args.rewire_otb:
        print("Rewiring OTB")
        create_rewired_graph("OM_OTB_201609", nswap_ecount_times=args.nswap_frac)

    if args.rewire_portal:
        print("Rewiring Portal")
        create_rewired_graph("OM_Portal_201510", nswap_ecount_times=args.nswap_frac)
