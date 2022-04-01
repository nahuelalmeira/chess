from pathlib import Path
from functools import partial
import pickle
from typing import Dict, Callable, List

import numpy as np
import pandas as pd
from cdlib.algorithms import leiden, label_propagation, louvain
from chessnet.graphs import read_pickle
from chessnet.utils import ARTIFACTS_DIR, Database


def get_algorithms(
    min_res: float = 0.1, max_res: float = 10, samples: int = 10
) -> Dict[str, Callable]:
    algorithms: Dict[str, Callable] = {
        "leiden": leiden,
        "label_propagation": label_propagation,
    }
    louvain_resolutions = np.logspace(np.log10(min_res), np.log10(max_res), samples)
    for resolution in louvain_resolutions:
        algorithms[f"louvain_{resolution:.4f}"] = partial(
            louvain, resolution=resolution
        )
    return algorithms


def compute_communities(
    database: str,
    min_res: float = 0.1,
    max_res: float = 10,
    samples: int = 10,
    overwrite: bool = False,
    verbose: bool = False,
):
    g = read_pickle(database)
    algorithms = get_algorithms(min_res=min_res, max_res=max_res, samples=samples)
    for name, func in algorithms.items():
        if verbose:
            print(database, name)
        filename = get_community_filename(database, name)
        if filename.is_file() and not overwrite:
            continue
        comms = func(g)
        pickle.dump(comms, open(filename, "wb"))


def load_communities(
    database: str,
    min_res: float = 0.1,
    max_res: float = 10,
    samples: int = 10,
    verbose: bool = False,
):
    algorithm_names = get_algorithms(
        min_res=min_res, max_res=max_res, samples=samples
    ).keys()
    communities = {}
    for name in algorithm_names:
        if verbose:
            print(name)
        filename = get_community_filename(database, name)
        if not filename.is_file():
            continue
        communities[name] = pickle.load(open(filename, "rb"))
    return communities


def get_community_filename(database: str, algorithm_name: str):
    return ARTIFACTS_DIR / f"{database}_{algorithm_name}.pickle"


def get_louvain_files(database: str, suffix: str) -> List[Path]:
    lst = []
    for filename in ARTIFACTS_DIR.iterdir():
        if filename.suffix != suffix:
            continue
        stem = filename.stem
        if database in stem and "louvain" in stem:
            lst.append(filename)
    return lst


def write_louvain_q_values(database):
    modularity_file = ARTIFACTS_DIR / f"{database}_louvain_modularities.csv"
    if modularity_file.is_file():
        df = pd.read_csv(modularity_file)
    else:
        df = pd.DataFrame(columns=["resolution", "q"])

    files = get_louvain_files(database, ".pickle")
    for filename in files:
        resolution = float(filename.stem.split("_")[-1])
        if resolution in df.resolution:
            continue
        comms = pickle.load(open(filename, "rb"))
        q = comms.newman_girvan_modularity().score
        df = df.append({"resolution": resolution, "q": q}, ignore_index=True)
    df.sort_values(by="resolution").to_csv(modularity_file)


if __name__ == "__main__":

    min_res = 0.1
    max_res = 100
    samples = 100
    overwrite = False
    verbose = True

    for database in [Database.OTB, Database.Portal]:
        compute_communities(
            database,
            min_res=min_res,
            max_res=max_res,
            samples=samples,
            overwrite=overwrite,
            verbose=verbose,
        )
