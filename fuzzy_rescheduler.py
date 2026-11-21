def triangular_membership(value, left, peak, right):
    """Return membership degree (0..1) for a triangular fuzzy set."""
    if value < left or value > right:
        return 0.0
    if value == peak:
        return 1.0
    if value < peak:
        return (value - left) / (peak - left) if peak != left else 1.0
    return (right - value) / (right - peak) if right != peak else 1.0

def progress_memberships(progress):
    x = max(0.0, min(100.0, float(progress)))
    return {
        "low": triangular_membership(x, 0, 0, 60),
        "medium": triangular_membership(x, 30, 60, 90),
        "high": triangular_membership(x, 60, 100, 100)
    }

def urgency_memberships(days_left):
    x = max(0.0, float(days_left))
    return {
        "low": triangular_membership(x, 7, 30, 60),
        "medium": triangular_membership(x, 2, 14, 30),
        "high": triangular_membership(x, 0, 0, 7)
    }

def fuzzy_time_factor(progress, days_until_exam):
    """Fuzzy IF-THEN rules and weighted-average defuzzification."""
    p, u = progress_memberships(progress), urgency_memberships(days_until_exam)
    rules = [
        (min(p["low"], u["high"]), 1.50),
        (min(p["low"], max(u["medium"], u["low"])), 1.25),
        (min(p["medium"], u["high"]), 1.25),
        (min(p["medium"], u["medium"]), 1.00),
        (min(p["medium"], u["low"]), 0.90),
        (p["high"], 0.75)
    ]
    strength = sum(weight for weight, _ in rules)
    return sum(weight * output for weight, output in rules) / strength if strength else 1.0

def reschedule(schedule, progress, available_hours_per_day, days_until_exam):
    """Remove completed topics; fuzzy rules adjust remaining study durations."""
    from datetime import date, timedelta
    capacity = float(available_hours_per_day)
    if capacity <= 0:
        raise ValueError("Available hours per day must be positive")

    tasks, decisions = [], []
    for task in schedule:
        name = task["topic"]
        done = max(0.0, min(100.0, float(progress.get(name, 0))))
        if done >= 100:
            continue
        factor = fuzzy_time_factor(done, days_until_exam)
        duration = max(0.5, round(
            float(task["duration_hours"]) * (100 - done) / 100 * factor, 2
        ))
        tasks.append({**task, "duration_hours": duration,
                      "progress": done, "fuzzy_time_factor": round(factor, 3)})
        decision = ("Increase study time" if factor > 1.05 else
                    "Reduce extra study time" if factor < 0.95 else
                    "Maintain approximately the same study time")
        decisions.append({"topic": name, "progress": done,
                          "fuzzy_time_factor": round(factor, 3),
                          "decision": decision})

    # Original schedule order is retained to respect prerequisite order.
    today, daily_load, updated = date.today(), {}, []
    for task in tasks:
        offset = 0
        while True:
            day = today + timedelta(days=offset)
            if daily_load.get(day, 0) + task["duration_hours"] <= capacity:
                break
            offset += 1
        daily_load[day] = daily_load.get(day, 0) + task["duration_hours"]
        updated.append({**task, "date": day.isoformat()})

    return {"updated_schedule": updated, "fuzzy_decisions": decisions,
            "completed_topics_removed": len(schedule) - len(tasks)}
