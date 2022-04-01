def elo_to_category(elo: float) -> str:
    if elo >= 2500:
        return "IG"
    elif 2400 <= elo < 2500:
        return "IM"
    elif 2300 <= elo < 2400:
        return "FM"
    elif 2200 <= elo < 2300:
        return "CM"
    elif 2000 <= elo < 2200:
        return "E"
    elif 1800 <= elo < 2200:
        return "CA"
    elif 1600 <= elo < 1800:
        return "CB"
    elif 1400 <= elo < 1600:
        return "CC"
    else:
        return "CD"