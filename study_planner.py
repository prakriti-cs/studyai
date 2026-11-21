from datetime import date, datetime, timedelta
from syllabus_analyzer import SyllabusKnowledgeBase

def parse_date(value, default):
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Use YYYY-MM-DD for dates") from exc

def heuristic_score(topic, exam_date, current_date):
    """Higher score = higher priority: importance, difficulty and urgency."""
    days_left = max((exam_date - current_date).days, 0)
    return 2 * topic["importance"] + 1.5 * topic["difficulty"] + 10 / (days_left + 1)

def generate_timetable(subjects, available_hours_per_day, start_date=None):
    """Greedy Best-First Search over topics whose prerequisites are complete."""
    capacity = float(available_hours_per_day)
    if capacity <= 0:
        raise ValueError("Available hours per day must be positive")
    if not subjects:
        raise ValueError("Provide at least one subject")

    today = date.today()
    start = parse_date(start_date, today)
    kb = SyllabusKnowledgeBase(subjects)
    exams = {
        s["name"]: parse_date(s.get("exam_date"), start + timedelta(days=30))
        for s in subjects
    }
    remaining, scheduled = set(kb.topics), set()
    daily_load, result = {}, []

    while remaining:
        eligible = [
            name for name in remaining
            if all(req in scheduled for req in kb.prerequisites[name])
        ]
        if not eligible:
            raise ValueError("No eligible topic; check prerequisite relationships")

        chosen = max(
            eligible,
            key=lambda name: heuristic_score(
                kb.topics[name], exams[kb.topic_subject[name]], start
            )
        )
        topic = kb.topics[chosen]
        offset = 0
        while True:
            day = start + timedelta(days=offset)
            if daily_load.get(day, 0) + topic["estimated_hours"] <= capacity:
                break
            offset += 1
            if offset > 365:
                raise ValueError("Could not fit topics within one year")

        daily_load[day] = daily_load.get(day, 0) + topic["estimated_hours"]
        result.append({
            "date": day.isoformat(), "subject": topic["subject"], "topic": chosen,
            "duration_hours": topic["estimated_hours"],
            "difficulty": topic["difficulty"], "importance": topic["importance"],
            "exam_date": exams[topic["subject"]].isoformat(),
            "priority_score": round(
                heuristic_score(topic, exams[topic["subject"]], start), 3
            ),
            "prerequisites": kb.prerequisites[chosen]
        })
        scheduled.add(chosen)
        remaining.remove(chosen)

    # Stable sort preserves prerequisite order when topics share a date.
    result.sort(key=lambda item: item["date"])
    return result
