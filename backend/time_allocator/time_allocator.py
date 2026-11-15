"""Smart study time allocator using expected-utility decision making.

Every topic offers a diminishing return on extra study time. The allocator
handles the budget one block at a time and always gives the next block to the
topic with the highest marginal expected utility, so each decision records the
option it beat and why.
"""
import math

MIN_GAIN = 1e-5


def _number(value, label, low=None, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{label} must be a number')
    if low is not None and value < low:
        raise ValueError(f'{label} must be at least {low}')
    if high is not None and value > high:
        raise ValueError(f'{label} must be at most {high}')
    return float(value)


def _prepare(topics):
    if not isinstance(topics, list) or not topics:
        raise ValueError('topics must be a nonempty list')
    prepared = []
    for topic in topics:
        if not isinstance(topic, dict) or not isinstance(topic.get('name'), str) or not topic['name'].strip():
            raise ValueError('each topic needs a name')
        prepared.append({
            'name': topic['name'].strip(),
            'mastery': _number(topic.get('mastery'), 'mastery', 0, 1),
            'weight': _number(topic.get('exam_weight', 1), 'exam_weight', 0.0001),
            'learning_rate': _number(topic.get('learning_rate', 0.6), 'learning_rate', 0.01, 5),
        })
    total_weight = sum(t['weight'] for t in prepared)
    for topic in prepared:
        topic['weight'] /= total_weight
    return prepared


def _mastery_at(topic, hours):
    """Diminishing-returns mastery curve for extra study hours."""
    return topic['mastery'] + (1.0 - topic['mastery']) * (1.0 - math.exp(-topic['learning_rate'] * hours))


def _marginal_utility(topic, hours, block_hours, risk_aversion):
    now = _mastery_at(topic, hours)
    after = _mastery_at(topic, hours + block_hours)
    gain = topic['weight'] * (after - now)
    # Risk aversion values time spent on weak topics slightly more, because
    # they carry the largest chance of dragging the final mark down.
    return gain * (1.0 + risk_aversion * (1.0 - now))


def allocate_study_time(topics, available_hours, block_minutes=15,
                        risk_aversion=0.3, max_hours_per_topic=None):
    """Allocate a study budget across topics by greedy marginal utility."""
    available_hours = _number(available_hours, 'available_hours', 0.01, 24 * 30)
    if isinstance(block_minutes, bool) or not isinstance(block_minutes, int) or not 5 <= block_minutes <= 120:
        raise ValueError('block_minutes must be an integer from 5 to 120')
    risk_aversion = _number(risk_aversion, 'risk_aversion', 0, 1)
    if max_hours_per_topic is not None:
        max_hours_per_topic = _number(max_hours_per_topic, 'max_hours_per_topic', 0.01)
    prepared = _prepare(topics)

    block_hours = block_minutes / 60.0
    total_blocks = int(math.floor(available_hours / block_hours + 1e-9))
    if total_blocks == 0:
        raise ValueError('available_hours is smaller than one study block')

    hours = [0.0] * len(prepared)
    blocks = [0] * len(prepared)
    decisions = []
    previous = None

    for block in range(total_blocks):
        best, best_utility, runner_up, runner_up_utility = None, -1.0, None, 0.0
        for i, topic in enumerate(prepared):
            if max_hours_per_topic is not None and hours[i] + block_hours > max_hours_per_topic + 1e-9:
                continue
            utility = _marginal_utility(topic, hours[i], block_hours, risk_aversion)
            if utility > best_utility + 1e-12:
                if best is not None:
                    runner_up, runner_up_utility = best, best_utility
                best, best_utility = i, utility
            elif runner_up is None or utility > runner_up_utility:
                runner_up, runner_up_utility = i, utility
        if best is None or best_utility < MIN_GAIN:
            break
        if best != previous and len(decisions) < 8:
            decisions.append({
                'block': block + 1,
                'chosen': prepared[best]['name'],
                'marginal_utility': round(best_utility, 5),
                'runner_up': prepared[runner_up]['name'] if runner_up is not None else None,
                'runner_up_utility': round(runner_up_utility, 5),
                'reason': 'highest expected grade gain for the next block'
                          + (' (risk-aversion bonus applied)' if risk_aversion > 0 else ''),
            })
        hours[best] += block_hours
        blocks[best] += 1
        previous = best

    allocations = []
    for i, topic in enumerate(prepared):
        before = topic['mastery']
        after = _mastery_at(topic, hours[i])
        allocations.append({
            'topic': topic['name'],
            'minutes': int(round(blocks[i] * block_minutes)),
            'share_of_budget': round(blocks[i] / total_blocks, 3),
            'mastery_before': round(before, 3),
            'mastery_after': round(after, 3),
            'expected_score_gain': round(topic['weight'] * (after - before), 4),
        })
    allocations.sort(key=lambda item: (-item['minutes'], item['topic']))

    used_blocks = sum(blocks)
    score_before = sum(t['weight'] * t['mastery'] for t in prepared)
    score_after = sum(t['weight'] * _mastery_at(t, hours[i]) for i, t in enumerate(prepared))
    skipped = [t['name'] for i, t in enumerate(prepared) if blocks[i] == 0]

    rationale = [
        'Each block goes to the topic with the highest marginal expected grade gain.',
        'Gains shrink as a topic improves, so the plan spreads time instead of over-studying one topic.',
    ]
    if risk_aversion > 0:
        rationale.append(f'Risk aversion {risk_aversion} gives weak topics a small extra priority.')
    if max_hours_per_topic is not None:
        rationale.append(f'No topic receives more than {max_hours_per_topic} hours.')
    if used_blocks < total_blocks:
        rationale.append('The remaining budget was left unallocated: extra study added almost no expected score.')

    return {
        'available_minutes': int(round(total_blocks * block_minutes)),
        'allocated_minutes': int(used_blocks * block_minutes),
        'unallocated_minutes': int((total_blocks - used_blocks) * block_minutes),
        'block_minutes': block_minutes,
        'allocations': allocations,
        'skipped_topics': skipped,
        'expected_score_before': round(score_before, 3),
        'expected_score_after': round(score_after, 3),
        'expected_score_gain': round(score_after - score_before, 3),
        'decisions': decisions,
        'rationale': rationale,
        'model': 'greedy marginal expected-utility allocation with diminishing returns',
    }


if __name__ == '__main__':
    import json
    demo = [
        {'name': 'Dynamic Programming', 'mastery': 0.3, 'exam_weight': 4, 'learning_rate': 0.5},
        {'name': 'Graphs', 'mastery': 0.45, 'exam_weight': 3, 'learning_rate': 0.7},
        {'name': 'Sorting', 'mastery': 0.9, 'exam_weight': 1, 'learning_rate': 1.0},
    ]
    print(json.dumps(allocate_study_time(demo, available_hours=4, block_minutes=30), indent=2))
