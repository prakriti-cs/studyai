import unittest
from backend.deadline_manager.deadline_manager import manage_deadlines
from backend.focus_optimizer.focus_optimizer import optimize_break
from backend.goal_tracker.goal_tracker import track_goal


class PlanningFeatureTests(unittest.TestCase):
    def test_deadlines(self):
        tasks = [{'name': 'Essay', 'deadline': '2026-11-17', 'estimated_hours': 6}]
        result = manage_deadlines(tasks, today='2026-11-15')
        self.assertEqual(result[0]['priority'], 'Critical')
        self.assertEqual(result[0]['days_left'], 2)

    def test_fuzzy(self):
        result = optimize_break(8, 7)
        self.assertTrue(5 <= result['break_minutes'] <= 20)
        self.assertTrue(result['rules_fired'])

    def test_goal(self):
        result = track_goal('Study AI', 20, 8, 5)
        self.assertEqual(result['progress_percentage'], 40)
        self.assertEqual(result['status'], 'Behind schedule')

    def test_invalid(self):
        with self.assertRaises(ValueError):
            optimize_break(11, 2)
        with self.assertRaises(ValueError):
            track_goal('X', 5, 6, 3)


if __name__ == '__main__':
    unittest.main()
