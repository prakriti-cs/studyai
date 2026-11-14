"""Academic goal tracker with transparent expert-system rules."""


def track_goal(goal, total_topics, completed_topics, days_left, hours_per_day=2, hours_per_topic=1):
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError('goal must be nonempty')
    for label, value in [('total_topics', total_topics), ('completed_topics', completed_topics), ('days_left', days_left)]:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f'{label} must be a nonnegative integer')
    if total_topics == 0 or completed_topics > total_topics:
        raise ValueError('total_topics must be positive and completed_topics cannot exceed it')
    for label, value in [('hours_per_day', hours_per_day), ('hours_per_topic', hours_per_topic)]:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f'{label} must be positive')
    remaining = total_topics - completed_topics
    progress = round(100 * completed_topics / total_topics, 2)
    pace = remaining / days_left if days_left > 0 else None
    required_hours = remaining * hours_per_topic
    available_hours = days_left * hours_per_day
    rules, advice = [], []
    if remaining == 0:
        status = 'Completed'
        rules.append('R1: All topics completed')
        advice.append('Goal complete. Review what you have learned.')
    elif days_left == 0:
        status = 'Deadline reached'
        rules.append('R2: Time remaining is zero')
        advice.append('Review unfinished topics and renegotiate the timeline.')
    elif required_hours > available_hours:
        status = 'Behind schedule'
        rules.append('R3: Required study hours exceed capacity')
        advice.append('Increase available hours, reduce scope or extend the deadline.')
    elif pace > 3:
        status = 'Intensive pace'
        rules.append('R4: More than 3 topics required daily')
        advice.append('Prioritize core topics and split the plan into short sessions.')
    else:
        status = 'On track'
        rules.append('R5: Goal is feasible within available hours')
        advice.append('Keep following your daily schedule.')
    if remaining and days_left:
        advice.append(f'Aim for {pace:.2f} topics per day ({required_hours:.1f} study hours remaining).')
    return {'goal': goal, 'progress_percentage': progress, 'remaining_topics': remaining,
            'days_left': days_left, 'required_study_hours': required_hours,
            'available_study_hours': available_hours, 'topics_per_day': round(pace, 2) if pace is not None else None,
            'status': status, 'advice': advice, 'rules_fired': rules}


if __name__ == '__main__':
    print(track_goal('Finish AI syllabus', 20, 8, 5, 2))
