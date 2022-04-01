from typing import Literal, Union
from black import InvalidInput

import pandas as pd
import igraph as ig
import networkx as nx

from chessnet.statistics import read_elo_data
from chessnet.utils import ARTIFACTS_DIR, Database
from chessnet.elo import elo_to_category


def edges_from_csv(
    database: str,
    drop_missing_elo: bool = True,
    min_elo: int = 500,
    max_elo: int = 4000,
) -> pd.DataFrame:
    df = pd.read_csv(ARTIFACTS_DIR / (database + ".csv"))
    if (database == Database.Portal) and ("Site" in df.columns):
        df = df[df.Site == "FICS freechess.org"]
    cols_to_dropna = ["White", "Black"]
    if drop_missing_elo:
        mask = (
            (df.WhiteElo >= min_elo)
            & (df.WhiteElo <= max_elo)
            & (df.BlackElo >= min_elo)
            & (df.BlackElo <= max_elo)
        )
        df = df[mask]
        cols_to_dropna += ["WhiteElo", "BlackElo"]
    df = df[cols_to_dropna].dropna()
    counts = df[["White", "Black"]].value_counts()
    counts.name = "NUMBER_OF_GAMES"
    edges = counts.reset_index()
    return edges


def csv_to_igraph(
    database: str, directed: bool = False, drop_missing_elo: bool = True
) -> ig.Graph:
    edges = edges_from_csv(database, drop_missing_elo=drop_missing_elo)
    g = ig.Graph.DataFrame(edges, directed=True)
    g = g.simplify(combine_edges="sum")
    if not directed:
        g.to_undirected(combine_edges="sum")
    print(g.vcount(), g.ecount())
    elo_data = read_elo_data(database)
    players = elo_data.index
    no_elo_players = [v.index for v in g.vs() if v["name"] not in players]
    g.delete_vertices(no_elo_players)
    print(g.vcount(), g.ecount())
    g.vs.select(_degree=0).delete()  # Remove isolates
    print(g.vcount(), g.ecount())
    players_elo = dict(elo_data.to_dict())
    g.vs["MeanElo"] = [players_elo["MeanElo"][v["name"]] for v in g.vs()]
    g.vs["StdElo"] = [players_elo["StdElo"][v["name"]] for v in g.vs()]
    g = g.components(mode="WEAK").giant()
    return g


def csv_to_networkx(
    database: str, directed: bool = False, drop_missing_elo: bool = True
) -> Union[nx.Graph, nx.DiGraph]:
    edges = edges_from_csv(database, drop_missing_elo=drop_missing_elo)
    g = nx.from_edgelist(
        edges.values, create_using=nx.DiGraph if directed else nx.Graph
    )
    print(g.number_of_nodes(), g.number_of_edges())
    elo_data = read_elo_data(database)
    players = elo_data.index
    no_elo_players = [v for v in g.nodes() if v not in players]
    g.remove_nodes_from(no_elo_players)
    print(g.number_of_nodes(), g.number_of_edges())
    g.remove_nodes_from(list(nx.isolates(g)))
    print(g.number_of_nodes(), g.number_of_edges())
    nx.set_node_attributes(g, elo_data["MeanElo"].to_dict(), "MeanElo")
    nx.set_node_attributes(g, elo_data["StdElo"].to_dict(), "StdElo")
    gcc = sorted(nx.connected_components(g), key=len, reverse=True)[0]
    g = g.subgraph(gcc)
    return g


def write_pickle(
    database: str,
    directed: bool = False,
    package: Literal["igraph", "networkx"] = "igraph",
):
    name = (
        database + ("_directed" if directed else "_undirected_") + package + ".pickle"
    )
    if package == "igraph":
        g = csv_to_igraph(database, directed=directed, drop_missing_elo=True)
        g.write_pickle(ARTIFACTS_DIR / name)
    elif package == "networkx":
        g = csv_to_networkx(database, directed=directed)
        nx.write_gpickle(g, ARTIFACTS_DIR / name)
    else:
        raise InvalidInput("Package must be in ['igraph', 'networkx']")


def read_pickle(
    database: str,
    directed: bool = False,
    package: Literal["igraph", "networkx"] = "igraph",
) -> Union[ig.Graph, nx.Graph, nx.DiGraph]:
    name = (
        database + ("_directed" if directed else "_undirected_") + package + ".pickle"
    )
    if package == "igraph":
        return ig.Graph.Read_Pickle(ARTIFACTS_DIR / name)
    elif package == "networkx":
        return nx.read_gpickle(ARTIFACTS_DIR / name)
    else:
        raise InvalidInput("Package must be in ['igraph', 'networkx']")


def get_players_degree(database: str, directed: bool = False) -> pd.DataFrame:
    g = read_pickle(database, directed=directed)
    node_df = pd.DataFrame(
        {
            "Player": [v["name"] for v in g.vs()],
            "k": [v.degree() for v in g.vs()],
        }
    ).set_index("Player")
    return node_df


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


def read_rewired_edgelist(database: str, nswap_ecount_times: float = 10.0) -> ig.Graph:
    name = f"{database}_rewired_f{nswap_ecount_times}.edgelist"
    filename = str(ARTIFACTS_DIR / name)
    g = ig.Graph.Read_Edgelist(filename, directed=False)
    return g


def read_rewired_graph(database: str, nswap_ecount_times: float = 10.0) -> ig.Graph:
    name = f"{database}_rewired_f{nswap_ecount_times}.pickle"
    filename = str(ARTIFACTS_DIR / name)
    g = ig.Graph.Read_Pickle(filename)
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


def _create_rewired_graph(database: str, nswap_ecount_times: float = 10.0):
    g = read_edgelist(database, directed=False, package="networkx")
    nswap = nswap_ecount_times * g.number_of_edges()
    max_tries = 10 * nswap
    h = nx.double_edge_swap(g, nswap=nswap, max_tries=max_tries)
    name = f"{database}_rewired_f{nswap_ecount_times}.edgelist"
    nx.write_edgelist(h, ARTIFACTS_DIR / name, data=False)


def create_rewired_graph(database: str, nswap_ecount_times: int = 10):
    g = read_pickle(database, directed=False, package="igraph")
    g = g.to_networkx()
    nswap = nswap_ecount_times * g.number_of_edges()
    max_tries = 10 * nswap
    g = nx.double_edge_swap(g, nswap=nswap, max_tries=max_tries)
    g = ig.Graph.from_networkx(g)
    name = f"{database}_rewired_f{nswap_ecount_times}.pickle"
    g.write_pickle(ARTIFACTS_DIR / name)


def write_degree_and_elo(database: str) -> None:
    df = get_players_degree(database).join(read_elo_data(database), how="inner")
    filename = ARTIFACTS_DIR / f"{database}_degree_and_elo.csv"
    df.to_csv(filename)


def read_degree_and_elo(database: str) -> pd.DataFrame:
    filename = ARTIFACTS_DIR / f"{database}_degree_and_elo.csv"
    return pd.read_csv(filename)


def write_gml(database: str, rewired: bool = False) -> None:
    g = (
        read_rewired_graph(database, nswap_ecount_times=10.0)
        if rewired
        else read_pickle(database)
    )
    gml_filename = database + ("_rewired" if rewired else "") + ".gml"
    g.vs["label"] = [elo_to_category(elo) for elo in g.vs["MeanElo"]]
    g.write_gml(str(ARTIFACTS_DIR / gml_filename))


def read_gml(database: str, rewired: bool = False) -> ig.Graph:
    gml_filename = database + ("_rewired" if rewired else "") + ".gml"
    return ig.Graph.Read_GML(str(ARTIFACTS_DIR / gml_filename))


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--parse-portal", action="store_true")
    parser.add_argument("--parse-otb", action="store_true")
    parser.add_argument("--directed", action="store_true")
    parser.add_argument("--pickle-portal", action="store_true")
    parser.add_argument("--pickle-otb", action="store_true")
    parser.add_argument("--randomize-portal", action="store_true")
    parser.add_argument("--randomize-otb", action="store_true")
    parser.add_argument("--rewire-portal", action="store_true")
    parser.add_argument("--rewire-otb", action="store_true")
    parser.add_argument("--degree-and-elo-otb", action="store_true")
    parser.add_argument("--degree-and-elo-portal", action="store_true")
    parser.add_argument("--gml-otb", action="store_true")
    parser.add_argument("--gml-portal", action="store_true")
    parser.add_argument("--gml-rewired-otb", action="store_true")
    parser.add_argument("--gml-rewired-portal", action="store_true")
    parser.add_argument("--nswap-frac", type=float, default=10)
    args = parser.parse_args()

    if args.pickle_otb:
        write_pickle("OM_OTB_201609", directed=args.directed, package="igraph")
        # write_pickle("OM_OTB_201609", directed=args.directed, package="networkx")

    if args.pickle_portal:
        write_pickle("OM_Portal_201510", directed=args.directed, package="igraph")
        # write_pickle("OM_Portal_201510", directed=args.directed, package="networkx")

    if args.parse_otb:
        csv_to_edgelist("OM_OTB_201609", directed=args.directed)

    if args.parse_portal:
        csv_to_edgelist("OM_Portal_201510", directed=args.directed)

    if args.degree_and_elo_otb:
        write_degree_and_elo("OM_OTB_201609")

    if args.degree_and_elo_portal:
        write_degree_and_elo("OM_Portal_201510")

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

    if args.gml_otb:
        write_gml("OM_OTB_201609")

    if args.gml_portal:
        write_gml("OM_Portal_201510")

    if args.gml_rewired_otb:
        write_gml("OM_OTB_201609", rewired=True)

    if args.gml_rewired_portal:
        write_gml("OM_Portal_201510", rewired=True)
