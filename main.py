import json
from pathlib import Path
from syllabus_analyzer import SyllabusKnowledgeBase
from study_planner import generate_timetable
from fuzzy_rescheduler import reschedule

SAMPLE = {
    "available_hours_per_day": 3,
    "start_date": "2026-11-17",
    "subjects": [{
        "name": "Artificial Intelligence",
        "exam_date": "2026-12-10",
        "units": ["Introduction", "Problem Solving"],
        "topics": [
            {"name": "Introduction to AI", "difficulty": 2,
             "importance": 3, "estimated_hours": 2},
            {"name": "Intelligent Agents", "difficulty": 3,
             "importance": 4, "estimated_hours": 2,
             "prerequisites": ["Introduction to AI"]},
            {"name": "Search Algorithms", "difficulty": 4,
             "importance": 5, "estimated_hours": 3,
             "prerequisites": ["Intelligent Agents"]}
        ]
    }]
}

def print_schedule(schedule):
    print("\nDATE       | SUBJECT                | TOPIC                  | HOURS")
    print("-" * 76)
    for item in schedule:
        print(f"{item['date']} | {item['subject'][:22]:22} | "
              f"{item['topic'][:22]:22} | {item['duration_hours']}")

def main():
    try:
        path = Path("syllabus.json")
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else SAMPLE
        subjects = data["subjects"]

        print("\n=== SMART SYLLABUS ANALYZER: KNOWLEDGE REPRESENTATION ===")
        knowledge = SyllabusKnowledgeBase(subjects)
        analysis = knowledge.analyze()
        print("Topics:", analysis["topic_count"])
        print("Prerequisites:", analysis["prerequisites"])
        print("Learning order:")
        for i, topic in enumerate(analysis["recommended_learning_order"], 1):
            print(f"{i}. {topic}")

        print("\n=== HEURISTIC SEARCH: STUDY TIMETABLE ===")
        schedule = generate_timetable(
            subjects, data.get("available_hours_per_day", 3), data.get("start_date")
        )
        print_schedule(schedule)

        if input("\nSimulate progress and fuzzy rescheduling? (y/n): ").strip().lower() == "y":
            progress = {}
            for item in schedule:
                value = input(f"Completion for {item['topic']} (0-100): ").strip()
                progress[item["topic"]] = float(value or 0)
            hours = input("New available hours per day [3]: ").strip()
            days = input("Days until next exam [10]: ").strip()
            result = reschedule(
                schedule, progress, float(hours or 3), float(days or 10)
            )
            print("\n=== FUZZY LOGIC DECISIONS ===")
            for decision in result["fuzzy_decisions"]:
                print(decision["topic"], "->", decision["decision"],
                      "(factor:", decision["fuzzy_time_factor"], ")")
            print_schedule(result["updated_schedule"])
        print("\nBackend run completed.")
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print("Input error:", error)

if __name__ == "__main__":
    main()
