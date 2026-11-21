"""Run the study planner from a single terminal entry point."""

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import Callable, NamedTuple, Optional

from backend.deadline_manager.deadline_manager import manage_deadlines
from backend.doubt_assistant.doubt_assistant import answer_doubt
from backend.exam_profiles import dbms
from backend.focus_optimizer.focus_optimizer import SHORT_SESSION_FATIGUE, optimize_break
from backend.goal_tracker.goal_tracker import track_goal
from backend.learning_path.learning_path import fastest_route, generate_learning_path
from backend.readiness_evaluator.readiness_evaluator import evaluate_readiness
from backend.resource_recommender.resource_recommender import recommend_resources
from backend.revision_scheduler.revision_scheduler import build_revision_schedule
from backend.time_allocator.time_allocator import allocate_study_time


REQUIRED = object()


class Field(NamedTuple):
    key: str
    label: str
    convert: Callable = str
    default: object = REQUIRED


class Command(NamedTuple):
    label: str
    run: Callable
    fields: tuple
    rows: tuple = ()
    display: Optional[Callable] = None


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("enter a finite number")
    return result


def iso_date(value):
    return date.fromisoformat(value).isoformat()


def yes_no(value):
    if value.lower() in {"y", "yes"}:
        return True
    if value.lower() in {"n", "no"}:
        return False
    raise ValueError("enter yes or no")


def split_items(value):
    return [item.strip() for item in value.split(";") if item.strip()]


def run_dbms_profile(days=dbms.DEFAULTS["days"], hours_per_day=dbms.DEFAULTS["hours_per_day"],
                     pass_mark=dbms.DEFAULTS["pass_mark"], target_retention=dbms.DEFAULTS["target_retention"],
                     simulations=dbms.DEFAULTS["simulations"], seed=dbms.DEFAULTS["seed"], mastery=None):
    dbms.run(argparse.Namespace(
        days=days, hours_per_day=hours_per_day, pass_mark=pass_mark,
        target_retention=target_retention, simulations=simulations, seed=seed, mastery=mastery,
    ))


def print_focus_plan(result):
    print(f"\nStudy for {result['study_minutes']} minutes, then take a {result['break_minutes']}-minute break.")
    print("\nWhy this plan?")
    for key in ("fatigue", "workload"):
        levels = " to ".join(
            level.lower() for level, strength in result[f"{key}_memberships"].items() if strength > 0
        )
        print(f"  {key.capitalize()} {result[key]:g}/10 falls in the {levels} range.")
    if result["fatigue"] >= SHORT_SESSION_FATIGUE:
        print(f"  A fatigue rating of {SHORT_SESSION_FATIGUE}/10 or higher calls for a shorter study session.")
    else:
        print(f"  Fatigue is below {SHORT_SESSION_FATIGUE}/10, so the standard study session applies.")

    print("\nBreak rules that matched")
    for rule in result["rules_fired"]:
        print(f"  - {rule['rule']} (match weight {rule['strength']:g})")
    print("  The break length is an average of these suggestions. Stronger matches count more.")


TOPIC_FIELDS = (Field("mastery", "Current mastery (0–1)", number, 0.5),
                Field("exam_weight", "Relative exam weight", number, 1.0))
COMMANDS = {
    "doubt": Command("Doubt Assistant", answer_doubt, (
        Field("query", "Question"),
        Field("subject", "Subject (optional)", default=None),
        Field("use_web", "Allow a Wikipedia lookup (yes/no)", yes_no, True),
    )),
    "recommend": Command("Resource Recommender", recommend_resources, (
        Field("query", "Topic or search query"),
        Field("level", "Level (optional)", default=None),
        Field("top_n", "Number of recommendations", int, 3),
    )),
    "learning-path": Command("Learning Path Generator", generate_learning_path, (
        Field("goal", "Learning goal"),
        Field("known_topics", "Known topics (separate with semicolons)", split_items, None),
        Field("hours_per_week", "Study hours per week (optional)", number, None),
    )),
    "route": Command("Fastest Learning Route", fastest_route, (
        Field("start", "Starting topic"),
        Field("goal", "Target topic"),
    )),
    "deadlines": Command("Deadline Manager", manage_deadlines, (
        Field("available_hours_per_day", "Available hours per day", number, 2.0),
    ), ("assignments", "assignment", (
        Field("deadline", "Deadline (YYYY-MM-DD)", iso_date),
        Field("estimated_hours", "Estimated hours", number, 1.0),
        Field("completed", "Already completed (yes/no)", yes_no, False),
    ))),
    "focus": Command("Focus Optimizer", optimize_break, (
        Field("fatigue", "Fatigue (0–10)", number),
        Field("workload", "Workload (0–10)", number),
    ), display=print_focus_plan),
    "goals": Command("Goal Tracker", track_goal, (
        Field("goal", "Study goal"),
        Field("total_topics", "Total topics", int),
        Field("completed_topics", "Completed topics", int),
        Field("days_left", "Days left", int),
        Field("hours_per_day", "Study hours per day", number, 2.0),
        Field("hours_per_topic", "Hours per topic", number, 1.0),
    )),
    "revision-schedule": Command("Revision Scheduler", build_revision_schedule, (
        Field("start_date", "Start date (YYYY-MM-DD, optional)", iso_date, None),
        Field("days", "Days to plan", int, 7),
        Field("minutes_per_day", "Revision minutes per day", int, 60),
        Field("target_retention", "Target retention (0–1)", number, 0.7),
    ), ("topics", "topic", (*TOPIC_FIELDS,
        Field("difficulty", "Difficulty (1–5)", number, 3.0),
        Field("last_studied", "Last studied (YYYY-MM-DD, optional)", iso_date, None),
    ))),
    "readiness": Command("Exam Readiness Evaluator", evaluate_readiness, (
        Field("pass_mark", "Pass mark (0–1)", number, 0.5),
    ), ("topics", "topic", (*TOPIC_FIELDS,
        Field("prerequisites", "Prerequisites (separate with semicolons)", split_items, None),
    ))),
    "allocate-time": Command("Study Time Allocator", allocate_study_time, (
        Field("available_hours", "Total study hours", number),
        Field("block_minutes", "Minutes per study block", int, 15),
    ), ("topics", "topic", (*TOPIC_FIELDS,
        Field("learning_rate", "Learning rate (0.01–5)", number, 0.6),
    ))),
    "dbms": Command("DBMS Syllabus Plan", run_dbms_profile, (
        Field("days", "Days to plan", int, dbms.DEFAULTS["days"]),
        Field("hours_per_day", "Study hours per day", number, dbms.DEFAULTS["hours_per_day"]),
        Field("pass_mark", "Pass mark (0–1)", number, dbms.DEFAULTS["pass_mark"]),
        Field("mastery", "Mastery overrides (Topic=0.7; optional)", split_items, None),
    )),
}


def ask(field):
    suffix = ""
    if field.default is not REQUIRED and field.default is not None:
        default = field.default
        if isinstance(default, bool):
            default = "yes" if default else "no"
        suffix = f" [{default}]"
    while True:
        raw = input(f"{field.label}{suffix}: ").strip()
        if not raw:
            if field.default is not REQUIRED:
                return field.default
            print("Please enter a value.", file=sys.stderr)
            continue
        try:
            return field.convert(raw)
        except ValueError as exc:
            print(f"Invalid {field.label.lower()}: {exc}", file=sys.stderr)


def prompt_inputs(command):
    payload = {field.key: ask(field) for field in command.fields}
    if command.rows:
        key, label, fields = command.rows
        rows = []
        name_field = Field("name", f"{label.capitalize()} name (blank when done)", default=None)
        while name := ask(name_field):
            rows.append({"name": name, **{field.key: ask(field) for field in fields}})
        payload[key] = rows
    return payload


def load_input(source):
    contents = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    payload = json.loads(contents)
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object")
    return payload


def run_command(command, source=None):
    try:
        payload = prompt_inputs(command) if source is None else load_input(source)
        result = command.run(**payload)
        if source is None and command.display is not None:
            command.display(result)
        elif result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"{command.label}: {exc}", file=sys.stderr)
        return 1
    return 0


def menu():
    choices = {str(index): name for index, name in enumerate(COMMANDS, 1)}
    while True:
        print("\nStudyAI")
        for number, name in choices.items():
            print(f"  {number:>2}. {COMMANDS[name].label}")
        print("   0. Exit")
        choice = input("Choose a feature: ").strip().lower()
        if choice in {"0", "q", "quit", "exit"}:
            return 0
        command = COMMANDS.get(choices.get(choice, choice))
        if command is None:
            print("Choose a feature from the menu.", file=sys.stderr)
        else:
            print(f"\n{command.label}")
            run_command(command)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m backend", description=__doc__)
    parser.add_argument("feature", choices=COMMANDS, nargs="?", help="omit to open the interactive menu")
    parser.add_argument("--input", metavar="FILE", help="read JSON input from a file or - for stdin")
    args = parser.parse_args(argv)
    if args.input is not None and args.feature is None:
        parser.error("--input requires a feature")
    try:
        if args.feature:
            return run_command(COMMANDS[args.feature], args.input)
        return menu()
    except EOFError:
        if args.feature:
            print("\nInput ended before the command could run.", file=sys.stderr)
            return 1
        print()
        return 0
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
