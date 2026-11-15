"""Revision scheduler driven by heuristic beam search over forgetting curves.

Every topic keeps a memory retention that decays exponentially (Ebbinghaus
curve). The planner simulates a window of study days; each day it may review a
set of topics, which resets their decay. Beam search explores those daily
choices and keeps the highest-scoring partial schedules, so the result comes
from a search over plans rather than a single greedy pass.
"""
import math
from datetime import date, timedelta

MAX_WINDOW_DAYS = 60
MAX_CANDIDATE_PLANS = 4
TIME_COST_PER_15_MINUTES = 0.01
DEFAULT_MASTERY = 0.5


def _number(value, label, low=None, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{label} must be a number')
    if low is not None and value < low:
        raise ValueError(f'{label} must be at least {low}')
    if high is not None and value > high:
        raise ValueError(f'{label} must be at most {high}')
    return float(value)


def _integer(value, label, low=None, high=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f'{label} must be an integer')
    if low is not None and value < low:
        raise ValueError(f'{label} must be at least {low}')
    if high is not None and value > high:
        raise ValueError(f'{label} must be at most {high}')
    return value


def _parse_date(value, label):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f'{label} must be YYYY-MM-DD') from exc
    raise ValueError(f'{label} must be YYYY-MM-DD')


def stability_days(mastery, difficulty):
    """Days until retention decays to about 37% of its value."""
    return max(0.5, (1.0 + 7.0 * mastery) * (1.2 - 0.1 * difficulty))


def retention_after(elapsed_days, stability):
    return math.exp(-max(float(elapsed_days), 0.0) / max(stability, 0.1))


def minutes_needed(difficulty, retention_now):
    """Reviews take longer the more has been forgotten."""
    cost = (15.0 + 4.0 * difficulty) * (1.0 + 0.6 * (1.0 - retention_now))
    return int(5 * math.ceil(cost / 5.0))


def _prepare(topics, start):
    if not isinstance(topics, list) or not topics:
        raise ValueError('topics must be a nonempty list')
    prepared = []
    for topic in topics:
        if not isinstance(topic, dict) or not isinstance(topic.get('name'), str) or not topic['name'].strip():
            raise ValueError('each topic needs a name')
        mastery = _number(topic.get('mastery', DEFAULT_MASTERY), 'mastery', 0, 1)
        difficulty = _number(topic.get('difficulty', 3), 'difficulty', 1, 5)
        weight = _number(topic.get('exam_weight', 1), 'exam_weight', 0.0001)
        last = topic.get('last_studied')
        last = start - timedelta(days=1) if last is None else _parse_date(last, 'last_studied')
        if last > start:
            raise ValueError('last_studied cannot be after start_date')
        prepared.append({
            'name': topic['name'].strip(),
            'mastery': mastery,
            'difficulty': difficulty,
            'weight': weight,
            'elapsed': float((start - last).days),
            'stability': stability_days(mastery, difficulty),
        })
    return prepared


def _urgency(topic, elapsed):
    retention = retention_after(elapsed, topic['stability'])
    return topic['weight'] * (1.0 - retention) * (0.6 + 0.1 * topic['difficulty'])


def _daily_options(state, prepared, minutes_per_day):
    """Greedy-ranked candidate review plans for one day (prefixes by urgency)."""
    order = sorted(range(len(prepared)),
                   key=lambda i: (-_urgency(prepared[i], state['elapsed'][i]), i))
    options = [([], 0.0)]
    plan, spent, gain = [], 0, 0.0
    for i in order:
        topic = prepared[i]
        retention = retention_after(state['elapsed'][i], topic['stability'])
        need = minutes_needed(topic['difficulty'], retention)
        remaining = minutes_per_day - spent
        if remaining <= 0:
            break
        minutes = min(need, remaining)
        if minutes < 10 and plan:
            continue
        gain += _urgency(topic, state['elapsed'][i]) * (minutes / need)
        spent += minutes
        plan.append((i, minutes, need))
        options.append((list(plan), gain - TIME_COST_PER_15_MINUTES * (spent / 15.0)))
        if len(options) >= MAX_CANDIDATE_PLANS:
            break
    return options


def _apply(state, prepared, day, plan, gain):
    new = {
        'elapsed': list(state['elapsed']),
        'mastery': list(state['mastery']),
        'stability': list(state['stability']),
        'score': state['score'] + gain,
        'plan': list(state['plan']),
    }
    if plan:
        sessions = []
        for i, minutes, need in plan:
            retention = retention_after(new['elapsed'][i], prepared[i]['stability'])
            before = new['mastery'][i]
            new['mastery'][i] = min(1.0, before + 0.05 * (1.0 - before) * (minutes / need))
            new['stability'][i] = stability_days(new['mastery'][i], prepared[i]['difficulty'])
            new['elapsed'][i] = 0
            sessions.append({
                'topic': prepared[i]['name'],
                'minutes': minutes,
                'retention_before': round(retention, 3),
                'mastery_before': round(before, 3),
                'mastery_after': round(new['mastery'][i], 3),
                'priority': round(_urgency(prepared[i], state['elapsed'][i]), 3),
            })
        new['plan'].append({'day': day, 'sessions': sessions,
                            'total_minutes': sum(s['minutes'] for s in sessions),
                            'heuristic_score': round(gain, 4)})
    new['elapsed'] = [e + 1.0 for e in new['elapsed']]
    return new


def _end_penalty(state, prepared, target_retention):
    return 2.0 * sum(topic['weight'] * max(
        0.0, target_retention - retention_after(state['elapsed'][i], state['stability'][i]))
        for i, topic in enumerate(prepared))


def build_revision_schedule(topics, start_date=None, days=7, minutes_per_day=60,
                            beam_width=5, target_retention=0.7):
    """Plan which topics to revise on each day using beam search."""
    start = _parse_date(start_date, 'start_date') if start_date is not None else date.today()
    days = _integer(days, 'days', 1, MAX_WINDOW_DAYS)
    minutes_per_day = _integer(minutes_per_day, 'minutes_per_day', 10, 24 * 60)
    beam_width = _integer(beam_width, 'beam_width', 1, 40)
    target_retention = _number(target_retention, 'target_retention', 0.3, 0.95)
    prepared = _prepare(topics, start)

    initial = {
        'elapsed': [t['elapsed'] for t in prepared],
        'mastery': [t['mastery'] for t in prepared],
        'stability': [t['stability'] for t in prepared],
        'score': 0.0,
        'plan': [],
    }
    beam = [initial]
    states_expanded = 0
    best_final, best_state = -1e9, None

    for day in range(days):
        scored = []
        for state in beam:
            for plan, gain in _daily_options(state, prepared, minutes_per_day):
                child = _apply(state, prepared, day, plan, gain)
                states_expanded += 1
                scored.append(child)
        scored.sort(key=lambda s: -s['score'])
        seen, beam = set(), []
        for state in scored:
            key = (tuple(round(e, 1) for e in state['elapsed']),
                   tuple(round(m, 3) for m in state['mastery']))
            if key in seen:
                continue
            seen.add(key)
            beam.append(state)
            if len(beam) >= beam_width:
                break
        for state in beam:
            final = state['score'] - _end_penalty(state, prepared, target_retention)
            if final > best_final:
                best_final, best_state = final, state

    plan_by_day = {entry['day']: entry for entry in best_state['plan']}
    schedule = []
    for day in range(days):
        entry = plan_by_day.get(day)
        schedule.append({
            'date': (start + timedelta(days=day)).isoformat(),
            'day': day + 1,
            'sessions': entry['sessions'] if entry else [],
            'total_minutes': entry['total_minutes'] if entry else 0,
            'heuristic_score': entry['heuristic_score'] if entry else 0.0,
        })

    coverage = {}
    for entry in best_state['plan']:
        for session in entry['sessions']:
            coverage[session['topic']] = coverage.get(session['topic'], 0) + 1
    skipped = [t['name'] for t in prepared if t['name'] not in coverage]
    total_sessions = sum(coverage.values())

    notes = []
    if skipped:
        notes.append('No review was worth the time for: ' + ', '.join(skipped))
    if total_sessions == 0:
        notes.append('Every topic is above the target retention for this window.')
    if any(s['total_minutes'] >= minutes_per_day for s in schedule):
        notes.append('Some days use the whole budget; raise minutes_per_day to cover more topics.')
    if best_state['plan']:
        notes.append('Search objective weights exam importance by how much each topic has decayed.')

    return {
        'start_date': start.isoformat(),
        'days': days,
        'minutes_per_day': minutes_per_day,
        'target_retention': target_retention,
        'schedule': schedule,
        'topic_coverage': coverage,
        'total_reviews': total_sessions,
        'final_retention': {
            t['name']: round(retention_after(best_state['elapsed'][i], best_state['stability'][i]), 3)
            for i, t in enumerate(prepared)},
        'search': {
            'algorithm': 'beam search over daily review plans',
            'heuristic': 'exam weight x forgetting urgency, minus a small time cost',
            'beam_width': beam_width,
            'states_expanded': states_expanded,
            'objective_score': round(best_final, 4),
            'retention_model': 'exponential forgetting curve',
            'notes': notes,
        },
    }


if __name__ == '__main__':
    from datetime import timedelta
    today = date.today()
    demo = [
        {'name': 'Binary Trees', 'mastery': 0.6, 'difficulty': 4, 'exam_weight': 1.5,
         'last_studied': (today - timedelta(days=4)).isoformat()},
        {'name': 'Graph Traversal', 'mastery': 0.3, 'difficulty': 3, 'exam_weight': 1.2,
         'last_studied': (today - timedelta(days=9)).isoformat()},
        {'name': 'Sorting', 'mastery': 0.9, 'difficulty': 2, 'exam_weight': 0.8,
         'last_studied': (today - timedelta(days=1)).isoformat()},
    ]
    import json
    print(json.dumps(build_revision_schedule(demo, days=5, minutes_per_day=90), indent=2))
