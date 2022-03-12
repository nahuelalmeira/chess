from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
FIGS_DIR = ROOT_DIR / "figures"


class Database:
    OTB = "OM_OTB_201609"
    Portal = "OM_Portal_201510"
