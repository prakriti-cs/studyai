def rising(x, start, end):
    if x <= start:
        return 0.0
    if x >= end:
        return 1.0
    return (x - start) / (end - start)


def falling(x, start, end):
    return 1.0 - rising(x, start, end)


def fuzzy_confidence(score):
    """Turns a similarity score into fuzzy low / medium / high memberships."""
    low = falling(score, 0.25, 0.40)
    medium = min(rising(score, 0.25, 0.40), falling(score, 0.40, 0.55))
    high = rising(score, 0.40, 0.55)

    memberships = {"low": low, "medium": medium, "high": high}
    label = max(memberships, key=memberships.get)
    return {"label": label, "low": round(low, 2), "medium": round(medium, 2), "high": round(high, 2)}
