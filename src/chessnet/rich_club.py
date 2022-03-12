from typing import List, Tuple, Optional

import igraph as ig
import numpy as np
import pandas as pd

from chessnet.graphs import read_edgelist, read_randomized_edgelist
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


def write_rich_club(database: str, samples: int = 100) -> None:
    g = read_edgelist(database)
    df = compute_rich_club(g, samples=samples)
    df.to_csv(ARTIFACTS_DIR / f"{database}_rich_club_samples{samples}.csv")


def read_rich_club(database: str, samples: int = 100) -> pd.DataFrame:
    return pd.read_csv(ARTIFACTS_DIR / f"{database}_rich_club_samples{samples}.csv")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--rich-club-otb", action="store_true")
    parser.add_argument("--rich-club-portal", action="store_true")
    args = parser.parse_args()

    if args.rich_club_otb:
        write_rich_club("OM_OTB_201609")

    if args.rich_club_otb:
        write_rich_club("OM_Portal_201510")
