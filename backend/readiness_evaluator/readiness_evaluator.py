"""Exam readiness evaluator using Bayesian belief + Monte Carlo reasoning.

Each topic's mastery is treated as a belief (Beta distribution) instead of a
fixed number. Prerequisite topics dampen the effective mastery of the topics
that depend on them, exam weights define how much each topic contributes to the
mark, and Monte Carlo simulation turns those beliefs into a probability of
passing, a credible score range and the topics that most raise the chances.
"""
import math
import random

DEFAULT_CONFIDENCE = 0.6
DEFAULT_PASS_MARK = 0.5
DEFAULT_SIMULATIONS = 2000
DEFAULT_SEED = 7
DEFAULT_EXAM_NOISE = 0.07
DEFAULT_IMPROVEMENT = 0.2


def _number(value, label, low=None, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{label} must be a number')
    if low is not None and value < low:
        raise ValueError(f'{label} must be at least {low}')
    if high is not None and value > high:
        raise ValueError(f'{label} must be at most {high}')
    return float(value)


def _clamp(value, low, high):
    return max(low, min(high, value))


def _beta_belief(mean, confidence):
    """Beta parameters with the given mean and a concentration from confidence."""
    mean = _clamp(mean, 0.005, 0.995)
    concentration = 6.0 + 18.0 * confidence
    return mean * concentration, (1.0 - mean) * concentration


def _prepare(topics):
    if not isinstance(topics, list) or not topics:
        raise ValueError('topics must be a nonempty list')
    prepared = []
    for topic in topics:
        if not isinstance(topic, dict) or not isinstance(topic.get('name'), str) or not topic['name'].strip():
            raise ValueError('each topic needs a name')
        prerequisites = topic.get('prerequisites') or []
        if isinstance(prerequisites, str):
            prerequisites = [prerequisites]
        if not isinstance(prerequisites, list) or not all(isinstance(p, str) for p in prerequisites):
            raise ValueError('prerequisites must be a list of topic names')
        prepared.append({
            'name': topic['name'].strip(),
            'mastery': _number(topic.get('mastery'), 'mastery', 0, 1),
            'weight': _number(topic.get('exam_weight', 1), 'exam_weight', 0.0001),
            'confidence': _number(topic.get('confidence', DEFAULT_CONFIDENCE), 'confidence', 0, 1),
            'prerequisites': [p.strip() for p in prerequisites if p.strip()],
        })
    return prepared


def _adjust_for_prerequisites(prepared):
    by_name = {t['name'].lower(): t for t in prepared}
    warnings, effective = [], []
    for topic in prepared:
        penalty, missing = 1.0, []
        for name in topic['prerequisites']:
            prerequisite = by_name.get(name.lower())
            if prerequisite is None:
                missing.append(name)
                continue
            penalty *= 0.55 + 0.45 * prerequisite['mastery']
        if missing:
            warnings.append(f"Unknown prerequisite(s) for {topic['name']}: {', '.join(missing)}")
        effective.append({
            'mastery': topic['mastery'] * penalty,
            'prerequisite_penalty': round(penalty, 3),
        })
    return effective, warnings


def _total_weight(prepared):
    return sum(t['weight'] for t in prepared)


def _simulate(prepared, effective, pass_mark, simulations, seed, bumped=None,
              exam_noise=DEFAULT_EXAM_NOISE, improvement=DEFAULT_IMPROVEMENT):
    rng = random.Random(seed)
    weights = [t['weight'] / _total_weight(prepared) for t in prepared]
    beliefs = []
    for i, topic in enumerate(prepared):
        mean = effective[i]['mastery'] + (improvement if bumped == i else 0.0)
        beliefs.append(_beta_belief(mean, topic['confidence']))
    scores, passes = [], 0
    for _ in range(simulations):
        base = 0.0
        for w, (alpha, beta) in zip(weights, beliefs):
            base += w * rng.betavariate(alpha, beta)
        # A shared paper-difficulty factor: one hard or easy paper shifts every
        # topic together, which is what gives near-threshold exams real spread.
        paper = _clamp(rng.gauss(1.0, exam_noise), 0.7, 1.35) if exam_noise else 1.0
        scores.append(_clamp(base * paper, 0.0, 1.0))
        if scores[-1] >= pass_mark:
            passes += 1
    return scores, passes / simulations


def _percentile(ordered, fraction):
    position = (len(ordered) - 1) * fraction
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def _band(probability):
    if probability >= 0.85:
        return 'Very likely'
    if probability >= 0.7:
        return 'Likely'
    if probability >= 0.5:
        return 'Borderline'
    if probability >= 0.3:
        return 'At risk'
    return 'Unlikely'


def evaluate_readiness(topics, pass_mark=DEFAULT_PASS_MARK, confidence=None,
                       simulations=DEFAULT_SIMULATIONS, seed=DEFAULT_SEED,
                       exam_noise=DEFAULT_EXAM_NOISE, improvement=DEFAULT_IMPROVEMENT):
    """Estimate the probability of passing an exam from topic-level beliefs."""
    pass_mark = _number(pass_mark, 'pass_mark', 0, 1)
    exam_noise = _number(exam_noise, 'exam_noise', 0, 0.3)
    improvement = _number(improvement, 'improvement', 0.05, 0.5)
    if isinstance(simulations, bool) or not isinstance(simulations, int) or not 300 <= simulations <= 20000:
        raise ValueError('simulations must be an integer from 300 to 20000')
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError('seed must be an integer')
    prepared = _prepare(topics)
    if confidence is not None:
        override = _number(confidence, 'confidence', 0, 1)
        for topic in prepared:
            topic['confidence'] = override
    effective, warnings = _adjust_for_prerequisites(prepared)

    scores, probability = _simulate(prepared, effective, pass_mark, simulations,
                                    seed, exam_noise=exam_noise)
    ordered = sorted(scores)
    mean_score = sum(scores) / len(scores)
    mc_error = 2.0 * math.sqrt(max(probability * (1 - probability), 0.0) / simulations)

    total_weight = _total_weight(prepared)
    breakdown = []
    for i, topic in enumerate(prepared):
        breakdown.append({
            'topic': topic['name'],
            'weight_fraction': round(topic['weight'] / total_weight, 3),
            'mastery': round(topic['mastery'], 3),
            'effective_mastery': round(effective[i]['mastery'], 3),
            'prerequisite_penalty': effective[i]['prerequisite_penalty'],
            'expected_contribution': round(topic['weight'] / total_weight * effective[i]['mastery'], 4),
        })

    leverage = []
    for i in range(len(prepared)):
        _, bumped_probability = _simulate(prepared, effective, pass_mark, simulations,
                                          seed, bumped=i, exam_noise=exam_noise,
                                          improvement=improvement)
        leverage.append({
            'topic': prepared[i]['name'],
            'current_probability': round(probability, 3),
            'probability_after_improvement': round(bumped_probability, 3),
            'expected_gain': round(bumped_probability - probability, 3),
            'expected_score_gain': round(
                prepared[i]['weight'] / total_weight
                * max(0.0, min(improvement, 1.0 - effective[i]['mastery'])), 4),
            'reason': f"raising {prepared[i]['name']} mastery by {int(improvement * 100)} points",
        })
    leverage.sort(key=lambda item: (-item['expected_gain'], item['topic']))

    if probability >= 0.85:
        advice = 'You are on track; keep short reviews so retention does not decay.'
    elif probability >= 0.6:
        advice = 'You can pass, but the margin is thin; reinforce the highest-leverage topics.'
    else:
        advice = 'Cover the highest-leverage topics first and reduce scope where possible.'

    return {
        'probability_pass': round(probability, 3),
        'readiness_band': _band(probability),
        'pass_mark': pass_mark,
        'exam_noise': exam_noise,
        'improvement_assumed': improvement,
        'expected_score': round(mean_score, 3),
        'score_credible_interval': {
            'low': round(_percentile(ordered, 0.05), 3),
            'median': round(_percentile(ordered, 0.5), 3),
            'high': round(_percentile(ordered, 0.95), 3),
        },
        'monte_carlo_error': round(mc_error, 3),
        'topic_breakdown': breakdown,
        'highest_leverage': leverage[:3],
        'prerequisite_notes': warnings,
        'advice': advice,
        'model': {
            'beliefs': 'Beta distribution per topic (mean = effective mastery, confidence = concentration)',
            'prerequisites': 'effective mastery multiplied by 0.55 + 0.45 x prerequisite mastery',
            'simulation': f'{simulations} Monte Carlo draws, seed {seed}',
            'probability': 'share of simulated exams scoring at or above the pass mark',
            'paper_difficulty': f'shared factor ~ Normal(1.0, {exam_noise}) clipped to 0.7-1.35',
            'assumptions': [
                'Topic mastery is independent between topics after prerequisite adjustment, '
                'apart from the shared paper-difficulty factor.',
                'Exam marks combine topic mastery linearly using the given exam weights.',
                'The mastery estimate is uncertain; confidence controls how wide that belief is.',
            ],
        },
    }


if __name__ == '__main__':
    import json
    demo = [
        {'name': 'Arrays', 'mastery': 0.85, 'exam_weight': 2},
        {'name': 'Binary Trees', 'mastery': 0.55, 'exam_weight': 3, 'prerequisites': ['Arrays']},
        {'name': 'Graphs', 'mastery': 0.35, 'exam_weight': 3,
         'prerequisites': ['Binary Trees'], 'confidence': 0.4},
        {'name': 'Dynamic Programming', 'mastery': 0.3, 'exam_weight': 4,
         'prerequisites': ['Arrays'], 'confidence': 0.5},
    ]
    print(json.dumps(evaluate_readiness(demo, pass_mark=0.6), indent=2))
