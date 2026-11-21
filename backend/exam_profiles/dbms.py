"""DBMS syllabus profile and tuned parameters for the three study planners.

Topic names, units and unit hours come from the course syllabus:

    UNIT-I    10 hours   concepts, architecture, data models, DBA, independence
    UNIT-II   11 hours   ER model, relational model, ER-to-relational, algebra, SQL
    UNIT-III  11 hours   functional dependencies, normalisation, decomposition,
                         transactions/ACID, concurrency control, recovery
    UNIT-IV   10 hours   database programming, NoSQL, MongoDB

Each topic's exam_weight is derived from its unit hours divided by the number
of topics in that unit: the syllabus has no per-topic marks, so hours are used
as a proxy for how much the exam is likely to lean on a topic. The mastery and
recency figures are assumed study-history values, not measured ones - change
them with `--mastery` or by editing TOPICS.

Run:
    python3.13 -m backend.exam_profiles.dbms
    python3.13 -m backend.exam_profiles.dbms --days 10 --hours-per-day 3
    python3.13 -m backend.exam_profiles.dbms --mastery "Relational Algebra=0.7"
"""
import argparse
from datetime import date, timedelta

from backend.readiness_evaluator.readiness_evaluator import evaluate_readiness
from backend.revision_scheduler.revision_scheduler import build_revision_schedule
from backend.time_allocator.time_allocator import allocate_study_time

UNIT_HOURS = {1: 10, 2: 11, 3: 11, 4: 10}

TOPICS = [
    # unit, name, assumed mastery, difficulty (1-5), learning_rate, prerequisites, days since last review
    (1, 'DBMS Concepts and Characteristics', 0.75, 2, 0.60, [], 12),
    (1, 'Database Architecture and Data Independence', 0.65, 3, 0.50, ['DBMS Concepts and Characteristics'], 12),
    (1, 'Data Models, Schemas and Instances', 0.60, 3, 0.50, ['DBMS Concepts and Characteristics'], 14),
    (1, 'File System vs DBMS, DBA and Users', 0.70, 2, 0.60, [], 15),

    (2, 'ER Model: Entities, Generalization, Aggregation', 0.55, 4, 0.40, ['Data Models, Schemas and Instances'], 10),
    (2, 'Relational Model and Constraints', 0.60, 3, 0.45, ['Data Models, Schemas and Instances'], 11),
    (2, 'ER to Relational Mapping', 0.50, 4, 0.35,
     ['ER Model: Entities, Generalization, Aggregation', 'Relational Model and Constraints'], 9),
    (2, 'Relational Algebra', 0.40, 4, 0.30, ['Relational Model and Constraints'], 18),
    (2, 'SQL: DDL, DML, Keys, Views, Indexes', 0.55, 3, 0.45, ['Relational Model and Constraints'], 8),

    (3, 'Functional Dependencies', 0.50, 4, 0.35, ['Relational Model and Constraints'], 16),
    (3, 'Normalization (1NF to 5NF)', 0.45, 5, 0.30, ['Functional Dependencies'], 17),
    (3, 'Lossless Join and Dependency Preserving Decomposition', 0.35, 5, 0.25,
     ['Normalization (1NF to 5NF)'], 20),
    (3, 'Transactions and ACID Properties', 0.60, 3, 0.50, ['Relational Model and Constraints'], 7),
    (3, 'Concurrency Control: Locks and Timestamps', 0.45, 5, 0.30, ['Transactions and ACID Properties'], 13),
    (3, 'Recovery, Logs, Checkpoints and Deadlocks', 0.40, 5, 0.30,
     ['Transactions and ACID Properties'], 13),

    (4, 'Database Programming: Cursors, Procedures, Triggers', 0.40, 4, 0.30, ['SQL: DDL, DML, Keys, Views, Indexes'], 6),
    (4, 'NoSQL Properties and Types', 0.50, 2, 0.60, [], 5),
    (4, 'MongoDB Basics', 0.45, 3, 0.50, ['NoSQL Properties and Types'], 4),
]

DEFAULTS = {
    'days': 14,
    'hours_per_day': 2.0,
    # 40 is the usual pass mark for a university theory paper; 0.55-0.60 is a
    # comfortable "safe" target and is printed alongside it.
    'pass_mark': 0.40,
    'confidence': 0.50,
    'exam_noise': 0.07,
    'improvement': 0.2,
    'target_retention': 0.75,
    'simulations': 4000,
    'seed': 7,
    'block_minutes': 30,
    'risk_aversion': 0.35,
    'max_hours_per_topic': 3.0,
    'beam_width': 6,
}


def _unit_topic_counts():
    counts = {}
    for unit, *_ in TOPICS:
        counts[unit] = counts.get(unit, 0) + 1
    return counts


def build_topics(start, mastery_overrides=None):
    """Turn the syllabus profile into the payloads the planners accept."""
    overrides = {}
    for item in mastery_overrides or []:
        if '=' not in item:
            raise ValueError(f"Bad mastery value {item!r}; expected 'Topic Name=0.7'")
        name, value = item.split('=', 1)
        overrides[name.strip().lower()] = float(value)
    counts = _unit_topic_counts()
    revision_topics, readiness_topics, allocator_topics = [], [], []
    for unit, name, mastery, difficulty, rate, prerequisites, days_ago in TOPICS:
        mastery = overrides.get(name.lower(), mastery)
        weight = round(UNIT_HOURS[unit] / counts[unit], 2)
        revision_topics.append({
            'name': name,
            'mastery': mastery,
            'difficulty': difficulty,
            'exam_weight': weight,
            'last_studied': (start - timedelta(days=days_ago)).isoformat(),
        })
        readiness_topics.append({
            'name': name,
            'mastery': mastery,
            'exam_weight': weight,
            'prerequisites': prerequisites,
            'confidence': DEFAULTS['confidence'],
        })
        allocator_topics.append({
            'name': name,
            'mastery': mastery,
            'exam_weight': weight,
            'learning_rate': rate,
        })
    return revision_topics, readiness_topics, allocator_topics


def run(args):
    start = date.today()
    days = args.days
    hours_per_day = args.hours_per_day
    revision_topics, readiness_topics, allocator_topics = build_topics(start, args.mastery)
    overridden = {o.split('=')[0].strip().lower() for o in (args.mastery or [])}

    print(f'DBMS syllabus plan - {len(TOPICS)} topics, {sum(UNIT_HOURS.values())} syllabus hours')
    print(f'start {start.isoformat()}, {days} days, {hours_per_day:g} h/day, '
          f'pass mark {args.pass_mark:.2f}\n')

    print('=== 1. Exam readiness (Bayesian beliefs + Monte Carlo) ===')
    readiness = evaluate_readiness(readiness_topics, pass_mark=args.pass_mark,
                                   simulations=args.simulations, seed=args.seed,
                                   exam_noise=DEFAULTS['exam_noise'],
                                   improvement=DEFAULTS['improvement'])
    print(f"P(pass at {args.pass_mark:.2f}) = {readiness['probability_pass']:.2f}"
          f"  ->  {readiness['readiness_band']}")
    print(f"expected score {readiness['expected_score']:.2f}, "
          f"90% credible range {readiness['score_credible_interval']['low']:.2f}"
          f"-{readiness['score_credible_interval']['high']:.2f} "
          f"(+/-{readiness['monte_carlo_error']:.3f} MC error)")
    for mark in (0.40, 0.50, 0.60, 0.70):
        alt = evaluate_readiness(readiness_topics, pass_mark=mark,
                                 simulations=args.simulations, seed=args.seed,
                                 exam_noise=DEFAULTS['exam_noise'],
                                 improvement=DEFAULTS['improvement'])
        print(f"  P(score >= {mark:.2f}) = {alt['probability_pass']:.2f}  ({alt['readiness_band']})")
    print('  highest leverage:')
    for item in readiness['highest_leverage']:
        print(f"    {item['topic']}: +{item['expected_gain']:.3f} probability "
              f"({item['current_probability']:.2f} -> {item['probability_after_improvement']:.2f}), "
              f"+{item['expected_score_gain']:.3f} score")
    weakest = sorted(readiness['topic_breakdown'], key=lambda t: t['effective_mastery'])[:4]
    print('  weakest effective mastery: ' + ', '.join(
        f"{t['topic']} {t['effective_mastery']:.2f}" for t in weakest))

    print('\n=== 2. Revision schedule (beam search over forgetting curves) ===')
    schedule = build_revision_schedule(
        revision_topics, start_date=start.isoformat(), days=days,
        minutes_per_day=int(hours_per_day * 60),
        beam_width=DEFAULTS['beam_width'], target_retention=args.target_retention)
    print(f"objective {schedule['search']['objective_score']}, "
          f"{schedule['search']['states_expanded']} states expanded, "
          f"{schedule['total_reviews']} reviews planned")
    for day in schedule['schedule']:
        topics = ', '.join(f"{s['topic']} ({s['minutes']}m)" for s in day['sessions'])
        print(f"  day {day['day']:>2} {day['date']}: {topics or 'no review needed'}")
    never = [name for name in (t['name'] for t in revision_topics)
             if name not in schedule['topic_coverage']]
    if never:
        print('  no review slot: ' + ', '.join(never))

    print('\n=== 3. Study time allocation (marginal expected utility) ===')
    allocation = allocate_study_time(
        allocator_topics, available_hours=days * hours_per_day,
        block_minutes=DEFAULTS['block_minutes'], risk_aversion=DEFAULTS['risk_aversion'],
        max_hours_per_topic=DEFAULTS['max_hours_per_topic'])
    print(f"budget {allocation['available_minutes']} min, allocated "
          f"{allocation['allocated_minutes']} min, left {allocation['unallocated_minutes']} min")
    for item in allocation['allocations']:
        if item['minutes']:
            print(f"  {item['topic']:<52} {item['minutes']:>4} min  "
                  f"mastery {item['mastery_before']:.2f}->{item['mastery_after']:.2f}  "
                  f"+{item['expected_score_gain']:.3f} score")
    if allocation['skipped_topics']:
        print('  skipped: ' + ', '.join(allocation['skipped_topics']))
    print(f"expected score {allocation['expected_score_before']:.2f} -> "
          f"{allocation['expected_score_after']:.2f} "
          f"(+{allocation['expected_score_gain']:.2f})")

    print('\n=== Tuned settings used ===')
    print(f"  readiness: pass_mark={args.pass_mark:.2f}, topic confidence="
          f"{DEFAULTS['confidence']}, exam_noise={DEFAULTS['exam_noise']}, "
          f"{args.simulations} simulations, seed {args.seed}")
    print(f"  scheduler: target_retention={args.target_retention:.2f}, beam_width="
          f"{DEFAULTS['beam_width']} (higher retention keeps more topics alive near exam week)")
    print(f"  allocator: {DEFAULTS['block_minutes']}-min blocks, risk_aversion="
          f"{DEFAULTS['risk_aversion']}, max {DEFAULTS['max_hours_per_topic']:g} h/topic")
    assumed = [t['name'] for t in readiness_topics if t['name'].lower() not in overridden]
    print(f"\n  Mastery is assumed for {len(assumed)} of {len(TOPICS)} topics; "
          "override with --mastery \"Topic Name=0.8\".")


def main():
    parser = argparse.ArgumentParser(description='Run the three study planners on the DBMS syllabus.')
    parser.add_argument('--days', type=int, default=DEFAULTS['days'])
    parser.add_argument('--hours-per-day', type=float, default=DEFAULTS['hours_per_day'])
    parser.add_argument('--pass-mark', type=float, default=DEFAULTS['pass_mark'])
    parser.add_argument('--target-retention', type=float, default=DEFAULTS['target_retention'])
    parser.add_argument('--simulations', type=int, default=DEFAULTS['simulations'])
    parser.add_argument('--seed', type=int, default=DEFAULTS['seed'])
    parser.add_argument('--mastery', nargs='*', metavar='NAME=VALUE',
                        help="override assumed mastery, e.g. --mastery 'Relational Algebra=0.7'")
    args = parser.parse_args()
    try:
        run(args)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
