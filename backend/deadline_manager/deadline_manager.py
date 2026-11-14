"""Explainable rule-based assignment and deadline prioritisation."""
from datetime import date


def manage_deadlines(assignments, today=None, available_hours_per_day=2):
    if not isinstance(assignments, list):
        raise ValueError('assignments must be a list')
    if isinstance(available_hours_per_day, bool) or not isinstance(available_hours_per_day, (int, float)) or available_hours_per_day <= 0:
        raise ValueError('available_hours_per_day must be positive')
    today = date.fromisoformat(today) if isinstance(today, str) else (today or date.today())
    results = []
    for task in assignments:
        if not isinstance(task, dict) or not isinstance(task.get('name'), str) or not task['name'].strip():
            raise ValueError('each assignment needs a name')
        try:
            due = date.fromisoformat(task['deadline'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('deadline must be YYYY-MM-DD') from exc
        hours = task.get('estimated_hours', 1)
        if isinstance(hours, bool) or not isinstance(hours, (int, float)) or hours < 0:
            raise ValueError('estimated_hours must be nonnegative')
        completed = task.get('completed', False)
        if not isinstance(completed, bool):
            raise ValueError('completed must be boolean')
        days_left = (due - today).days
        if completed:
            priority, rules, advice = 'Completed', ['R1: Completed task'], ['No further action required.']
        elif days_left < 0:
            priority, rules, advice = 'Overdue', ['R2: Deadline passed'], ['Contact your instructor and complete the task as soon as possible.']
        elif days_left <= 2:
            priority, rules, advice = 'Critical', ['R3: Due within 2 days'], ['Prioritize this assignment today.']
        elif days_left <= 7:
            priority, rules, advice = 'High', ['R4: Due within 7 days'], ['Allocate time to this assignment this week.']
        else:
            priority, rules, advice = 'Normal', ['R5: More than 7 days remain'], ['Schedule regular work sessions.']
        if not completed and hours > max(days_left, 0) * available_hours_per_day:
            rules.append('R6: Estimated work exceeds remaining capacity')
            advice.append('Split into smaller tasks or revise your available study hours.')
        results.append({'assignment': task['name'], 'deadline': due.isoformat(), 'days_left': days_left,
                        'estimated_hours': hours, 'priority': priority, 'advice': advice, 'rules_fired': rules})
    rank = {'Overdue': 0, 'Critical': 1, 'High': 2, 'Normal': 3, 'Completed': 4}
    return sorted(results, key=lambda x: (rank[x['priority']], x['days_left']))


if __name__ == '__main__':
    from datetime import timedelta
    today = date.today()
    print(manage_deadlines([{'name': 'AI Project', 'deadline': (today + timedelta(days=1)).isoformat(), 'estimated_hours': 6},
                            {'name': 'DBMS Lab', 'deadline': (today + timedelta(days=6)).isoformat()}]))
