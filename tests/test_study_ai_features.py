import unittest

from backend.revision_scheduler.revision_scheduler import build_revision_schedule
from backend.readiness_evaluator.readiness_evaluator import evaluate_readiness
from backend.time_allocator.time_allocator import allocate_study_time


class RevisionSchedulerTests(unittest.TestCase):
    topics = [
        {'name': 'Decayed', 'mastery': 0.4, 'difficulty': 4, 'exam_weight': 2,
         'last_studied': '2026-11-01'},
        {'name': 'Fresh', 'mastery': 0.9, 'difficulty': 2, 'exam_weight': 1,
         'last_studied': '2026-11-14'},
    ]

    def test_budget_is_respected(self):
        result = build_revision_schedule(self.topics, start_date='2026-11-15',
                                         days=4, minutes_per_day=60, beam_width=3)
        self.assertEqual(len(result['schedule']), 4)
        for day in result['schedule']:
            self.assertLessEqual(day['total_minutes'], 60)
        self.assertEqual(result['search']['algorithm'], 'beam search over daily review plans')

    def test_decayed_topic_is_reviewed_more(self):
        result = build_revision_schedule(self.topics, start_date='2026-11-15',
                                         days=7, minutes_per_day=90)
        coverage = result['topic_coverage']
        self.assertGreater(coverage.get('Decayed', 0), coverage.get('Fresh', 0))

    def test_deterministic_and_errors(self):
        first = build_revision_schedule(self.topics, start_date='2026-11-15', days=3)
        second = build_revision_schedule(self.topics, start_date='2026-11-15', days=3)
        self.assertEqual(first['topic_coverage'], second['topic_coverage'])
        with self.assertRaises(ValueError):
            build_revision_schedule([], start_date='2026-11-15')
        with self.assertRaises(ValueError):
            build_revision_schedule([{'name': 'X', 'mastery': 1.5}], start_date='2026-11-15')
        with self.assertRaises(ValueError):
            build_revision_schedule(self.topics, start_date='2026-11-15', days=0)


class ReadinessEvaluatorTests(unittest.TestCase):
    topics = [
        {'name': 'Arrays', 'mastery': 0.8, 'exam_weight': 2},
        {'name': 'Trees', 'mastery': 0.5, 'exam_weight': 3, 'prerequisites': ['Arrays']},
        {'name': 'Graphs', 'mastery': 0.4, 'exam_weight': 3, 'prerequisites': ['Trees']},
    ]

    def test_probability_range_and_band(self):
        result = evaluate_readiness(self.topics, pass_mark=0.5, simulations=600)
        self.assertGreaterEqual(result['probability_pass'], 0)
        self.assertLessEqual(result['probability_pass'], 1)
        self.assertIn(result['readiness_band'],
                      ['Very likely', 'Likely', 'Borderline', 'At risk', 'Unlikely'])
        self.assertLessEqual(result['score_credible_interval']['low'],
                             result['score_credible_interval']['high'])

    def test_better_mastery_increases_probability(self):
        weak = evaluate_readiness(self.topics, pass_mark=0.6, simulations=800)
        strong_topics = [dict(topic, mastery=min(1.0, topic['mastery'] + 0.4)) for topic in self.topics]
        strong = evaluate_readiness(strong_topics, pass_mark=0.6, simulations=800)
        self.assertGreater(strong['probability_pass'], weak['probability_pass'])
        self.assertGreater(strong['expected_score'], weak['expected_score'])

    def test_prerequisite_gap_lowers_effective_mastery(self):
        result = evaluate_readiness(self.topics, simulations=400)
        graphs = next(t for t in result['topic_breakdown'] if t['topic'] == 'Graphs')
        self.assertLess(graphs['effective_mastery'], graphs['mastery'])
        self.assertLess(graphs['prerequisite_penalty'], 1.0)

    def test_exam_noise_grades_near_threshold_probability(self):
        sharp = evaluate_readiness(self.topics, pass_mark=0.55, simulations=1500, exam_noise=0)
        noisy = evaluate_readiness(self.topics, pass_mark=0.55, simulations=1500, exam_noise=0.2)
        self.assertGreater(noisy['probability_pass'], sharp['probability_pass'])
        self.assertGreater(noisy['score_credible_interval']['high'],
                           noisy['score_credible_interval']['low'])
        with self.assertRaises(ValueError):
            evaluate_readiness(self.topics, exam_noise=0.5)
        with self.assertRaises(ValueError):
            evaluate_readiness(self.topics, improvement=0)

    def test_seed_and_leverage(self):
        first = evaluate_readiness(self.topics, simulations=500, seed=11)
        second = evaluate_readiness(self.topics, simulations=500, seed=11)
        self.assertEqual(first['probability_pass'], second['probability_pass'])
        self.assertEqual(len(first['highest_leverage']), 3)
        self.assertGreaterEqual(first['highest_leverage'][0]['expected_gain'],
                                first['highest_leverage'][-1]['expected_gain'])
        self.assertTrue(all('expected_score_gain' in item for item in first['highest_leverage']))

    def test_errors(self):
        with self.assertRaises(ValueError):
            evaluate_readiness([])
        with self.assertRaises(ValueError):
            evaluate_readiness([{'name': 'X', 'mastery': 0.5}], pass_mark=1.5)
        with self.assertRaises(ValueError):
            evaluate_readiness([{'name': 'X', 'mastery': 0.5}], simulations=10)


class TimeAllocatorTests(unittest.TestCase):
    topics = [
        {'name': 'DP', 'mastery': 0.3, 'exam_weight': 4},
        {'name': 'Graphs', 'mastery': 0.5, 'exam_weight': 2},
        {'name': 'Sorting', 'mastery': 0.95, 'exam_weight': 1},
    ]

    def test_budget_and_blocks(self):
        result = allocate_study_time(self.topics, available_hours=3, block_minutes=30)
        self.assertEqual(result['allocated_minutes'], 180)
        self.assertEqual(sum(a['minutes'] for a in result['allocations']), 180)
        for allocation in result['allocations']:
            self.assertEqual(allocation['minutes'] % 30, 0)

    def test_high_weight_topic_gets_more_time(self):
        result = allocate_study_time(self.topics, available_hours=3, block_minutes=15)
        minutes = {a['topic']: a['minutes'] for a in result['allocations']}
        self.assertGreater(minutes['DP'], minutes['Graphs'])
        self.assertGreater(result['expected_score_after'], result['expected_score_before'])
        self.assertTrue(result['decisions'])

    def test_saturated_topic_is_skipped(self):
        result = allocate_study_time([{'name': 'Done', 'mastery': 1.0, 'exam_weight': 1}],
                                     available_hours=2, block_minutes=30)
        self.assertIn('Done', result['skipped_topics'])
        self.assertGreater(result['unallocated_minutes'], 0)

    def test_errors(self):
        with self.assertRaises(ValueError):
            allocate_study_time(self.topics, available_hours=0)
        with self.assertRaises(ValueError):
            allocate_study_time([], available_hours=2)
        with self.assertRaises(ValueError):
            allocate_study_time(self.topics, available_hours=2, block_minutes=0)


if __name__ == '__main__':
    unittest.main()
