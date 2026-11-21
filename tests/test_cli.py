import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from backend.cli import COMMANDS, main


class TerminalTests(unittest.TestCase):
    def run_cli(self, args, user_input=""):
        output, errors = io.StringIO(), io.StringIO()
        with patch("sys.stdin", io.StringIO(user_input)), redirect_stdout(output), redirect_stderr(errors):
            code = main(args)
        return code, output.getvalue(), errors.getvalue()

    def test_each_feature_runs_without_a_server(self):
        topic = {"name": "Arrays", "mastery": 0.4}
        examples = {
            "doubt": {"query": "what is bfs", "use_web": False},
            "recommend": {"query": "graph traversal"},
            "learning-path": {"goal": "BFS"},
            "route": {"start": "Arrays", "goal": "BFS"},
            "deadlines": {"assignments": [{"name": "Lab", "deadline": "2026-11-22"}]},
            "focus": {"fatigue": 8, "workload": 7},
            "goals": {"goal": "Revise AI", "total_topics": 5, "completed_topics": 1, "days_left": 3},
            "revision-schedule": {"topics": [topic], "days": 2},
            "readiness": {"topics": [topic], "simulations": 300},
            "allocate-time": {"topics": [topic], "available_hours": 2},
            "dbms": {"days": 1, "simulations": 300},
        }
        self.assertEqual(examples.keys(), COMMANDS.keys())
        for feature, payload in examples.items():
            with self.subTest(feature=feature):
                code, output, errors = self.run_cli([feature, "--input", "-"], json.dumps(payload))
                self.assertEqual(code, 0, errors)
                if feature == "dbms":
                    self.assertIn("DBMS syllabus plan", output)
                else:
                    self.assertTrue(json.loads(output))

    def test_menu_retries_invalid_input_and_returns_after_a_feature(self):
        code, output, errors = self.run_cli([], "9\n\nArrays\nwrong\n0.7\n\n\n\n0\n")
        self.assertEqual(code, 0)
        self.assertIn("invalid current mastery", errors.lower())
        self.assertIn('"probability_pass"', output)
        self.assertEqual(output.count("Choose a feature"), 2)

    def test_invalid_json_input_has_an_actionable_error(self):
        code, output, errors = self.run_cli(["focus", "--input", "-"], "[]")
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("input must be a JSON object", errors)

    def test_doubt_menu_explains_bfs_and_what_the_match_score_means(self):
        code, output, errors = self.run_cli([], "1\nWhat is BFS?\n\nno\n0\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("A → B → C → D", output)
        self.assertIn("Match confidence — Medium", output)
        self.assertIn("how closely your wording matches the saved question", output)
        self.assertNotIn('"similarity_score"', output)

    def test_doubt_shows_the_wikipedia_source_for_a_fallback_answer(self):
        summary = {"title": "Example topic", "answer": "An example summary.", "link": "https://example.org/topic"}
        with patch("backend.doubt_assistant.doubt_assistant.wikipedia_summary", return_value=summary):
            code, output, errors = self.run_cli(["doubt"], "zzzzzzqxy\n\nyes\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Source — Wikipedia", output)
        self.assertIn(summary["link"], output)

    def test_doubt_offers_suggestions_when_no_answer_matches(self):
        code, output, errors = self.run_cli(["doubt"], "zzzzzzqxy\n\nno\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("could not find a relevant answer", output)
        self.assertIn("Try asking about", output)

    def test_focus_menu_explains_the_plan_without_printing_json(self):
        code, output, errors = self.run_cli([], "6\n8\n7\n0\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Study for 25 minutes, then take a 20-minute break.", output)
        self.assertIn("Workload 7/10 falls in the medium to high range.", output)
        self.assertIn("Stronger matches count more.", output)
        self.assertNotIn('"fatigue_memberships"', output)

    def test_focus_json_preserves_the_recommendation_and_rules(self):
        code, output, errors = self.run_cli(["focus", "--input", "-"], '{"fatigue":8,"workload":7}')
        self.assertEqual(code, 0, errors)
        result = json.loads(output)
        self.assertEqual((result["study_minutes"], result["break_minutes"]), (25, 20))
        self.assertEqual(len(result["rules_fired"]), 2)

    def test_bad_dbms_mastery_does_not_close_the_menu(self):
        code, output, errors = self.run_cli([], "dbms\n\n\n\ninvalid\n0\n")
        self.assertEqual(code, 0)
        self.assertIn("expected 'Topic Name=0.7'", errors)
        self.assertEqual(output.count("Choose a feature"), 2)
