"""Explainable zero-dependency Sugeno fuzzy break recommender."""


def triangle(x, a, b, c):
    if not a <= b <= c:
        raise ValueError('triangle coordinates must be ordered')
    if x < a or x > c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a) if b > a else 1.0
    return (c - x) / (c - b) if c > b else 1.0


def fuzzy_levels(x):
    return {'Low': triangle(x, 0, 0, 5),
            'Medium': triangle(x, 2, 5, 8),
            'High': triangle(x, 5, 10, 10)}


def optimize_break(fatigue, workload):
    for label, value in [('fatigue', fatigue), ('workload', workload)]:
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not 0 <= value <= 10:
            raise ValueError(f'{label} must be a number from 0 to 10')
    f, w = fuzzy_levels(fatigue), fuzzy_levels(workload)
    rules = {
        ('Low', 'Low'): 5, ('Low', 'Medium'): 5, ('Low', 'High'): 10,
        ('Medium', 'Low'): 10, ('Medium', 'Medium'): 10, ('Medium', 'High'): 15,
        ('High', 'Low'): 15, ('High', 'Medium'): 20, ('High', 'High'): 20
    }
    fired = []
    weighted = strength_sum = 0.0
    for (fl, wl), minutes in rules.items():
        strength = min(f[fl], w[wl])
        if strength > 0:
            fired.append({'rule': f'IF fatigue {fl} AND workload {wl} THEN break {minutes} minutes',
                          'strength': round(strength, 3)})
            weighted += strength * minutes
            strength_sum += strength
    if strength_sum == 0:
        raise ValueError('No fuzzy rule activated')
    return {'fatigue': fatigue, 'workload': workload,
            'fatigue_memberships': f, 'workload_memberships': w,
            'break_minutes': round(weighted / strength_sum),
            'study_minutes': 25 if fatigue >= 7 else 45,
            'inference': 'Sugeno weighted average with minimum AND', 'rules_fired': fired}


if __name__ == '__main__':
    print(optimize_break(8, 7))
