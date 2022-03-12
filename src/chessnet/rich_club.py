import copy
from typing import List, Tuple, Optional

import igraph as ig
import numpy as np
import pandas as pd

from chessnet.graphs import read_pickle
from chessnet.utils import ARTIFACTS_DIR


def compute_rich_club(g: ig.Graph, samples: int = 100) -> pd.DataFrame:
    degrees, densities = rich_club(g, samples=samples)
    _, rand_densities = rich_club(
        ig.Graph.Degree_Sequence(g.degree(), method="vl"),
        samples=samples,
        degrees=degrees,
    )
    df = pd.DataFrame({"k": degrees, "phi": densities, "rand_phi": rand_densities})
    df["rho"] = df.phi / df.rand_phi
    return df


def compute_rich_club_elo(g: ig.Graph, samples: int = 100) -> pd.DataFrame:
    # degree_and_elo = [(v.degree(), v["MeanElo"]) for v in g.vs()]
    # sorted_elo = list(zip(*sorted(degree_and_elo, key=lambda x: x[0])))[1]
    # h = ig.Graph.Degree_Sequence(g.degree(), method="vl")
    # sorted_nodes = list(
    #    zip(*sorted([(v.degree(), v.index) for v in h.vs()], key=lambda x: x[0]))
    # )[1]
    # mean_elo = [0] * h.vcount()
    # for index, elo in zip(sorted_nodes, sorted_elo):
    #    mean_elo[index] = elo
    # h.vs["MeanElo"] = mean_elo
    h = copy.deepcopy(g)
    shuffled_elo = g.vs["MeanElo"]
    np.random.shuffle(shuffled_elo)
    h.vs["MeanElo"] = shuffled_elo
    elo_values, densities = rich_club_elo(g, samples=samples)
    _, rand_densities = rich_club_elo(
        h,
        samples=samples,
        elo_values=elo_values,
    )
    df = pd.DataFrame({"elo": elo_values, "phi": densities, "rand_phi": rand_densities})
    df["rho"] = df.phi / df.rand_phi
    return df


def rich_club(
    g: ig.Graph, samples: int = 100, degrees: Optional[List[int]] = None
) -> Tuple[List[int], List[float]]:
    mink = min(g.degree())
    maxk = max(g.degree())
    density_values = []
    if degrees is None:
        degrees = list(
            np.logspace(np.log10(mink), np.log10(maxk - 1), samples, endpoint=True)
        )
    for k in degrees:
        subgraph_nodes = g.vs.select(_degree_gt=k)
        h = g.subgraph(subgraph_nodes)
        m = h.ecount()
        n = h.vcount()
        density = m / (n * (n - 1) / 2) if n > 1 else np.nan
        density_values.append(density)
    return degrees, density_values


def rich_club_elo(
    g: ig.Graph, samples: int = 100, elo_values: Optional[List[int]] = None
) -> Tuple[List[int], List[float]]:
    min_elo = min(g.vs["MeanElo"])
    max_elo = max(g.vs["MeanElo"])
    density_values = []
    if elo_values is None:
        elo_values = list(np.linspace(min_elo, max_elo - 1, samples, endpoint=True))
    for elo in elo_values:
        subgraph_nodes = g.vs.select(MeanElo_gt=elo)
        h = g.subgraph(subgraph_nodes)
        m = h.ecount()
        n = h.vcount()
        density = m / (n * (n - 1) / 2) if n > 1 else np.nan
        density_values.append(density)
    return elo_values, density_values


def write_rich_club(database: str, samples: int = 100) -> None:
    g = read_pickle(database)
    df = compute_rich_club(g, samples=samples)
    df.to_csv(ARTIFACTS_DIR / f"{database}_rich_club_samples{samples}.csv")


def read_rich_club(database: str, samples: int = 100) -> pd.DataFrame:
    return pd.read_csv(
        ARTIFACTS_DIR / f"{database}_rich_club_samples{samples}.csv"
    ).dropna()


def write_rich_club_elo(database: str, samples: int = 100) -> None:
    g = read_pickle(database)
    df = compute_rich_club_elo(g, samples=samples)
    df.to_csv(ARTIFACTS_DIR / f"{database}_rich_club_elo_samples{samples}.csv")


def read_rich_club_elo(database: str, samples: int = 100) -> pd.DataFrame:
    return pd.read_csv(ARTIFACTS_DIR / f"{database}_rich_club_elo_samples{samples}.csv")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--rich-club-otb", action="store_true")
    parser.add_argument("--rich-club-portal", action="store_true")
    parser.add_argument("--rich-club-elo-otb", action="store_true")
    parser.add_argument("--rich-club-elo-portal", action="store_true")
    parser.add_argument("--samples", type=int, default=30)
    args = parser.parse_args()

    if args.rich_club_otb:
        write_rich_club("OM_OTB_201609", samples=args.samples)

    if args.rich_club_otb:
        write_rich_club("OM_Portal_201510", samples=args.samples)

    if args.rich_club_elo_otb:
        write_rich_club_elo("OM_OTB_201609", samples=args.samples)

    if args.rich_club_elo_otb:
        write_rich_club_elo("OM_Portal_201510", samples=args.samples)
