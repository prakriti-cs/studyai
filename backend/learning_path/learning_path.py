import heapq
from collections import deque

from shared.database.topics_data import TOPICS
from shared.common.topic_search import match_topics, get_topic_resources
from backend.learning_path.expert_system import run_expert_system

# topic -> topics that must be learned before it
TOPIC_GRAPH = {name: data["prerequisites"] for name, data in TOPICS.items()}

# topic -> topics it unlocks (the same graph, other direction)
UNLOCKS = {name: [] for name in TOPICS}
for name, prereqs in TOPIC_GRAPH.items():
    for prereq in prereqs:
        UNLOCKS[prereq].append(name)

MIN_HOURS = min(data["hours"] for data in TOPICS.values())

GENERAL_SUBTOPICS = ["Basic terms and definitions", "Core concepts", "Worked examples",
                     "Practice questions", "Revision and summary notes"]


def find_topic(name):
    for topic in TOPIC_GRAPH:
        if topic.lower() == name.strip().lower():
            return topic

    _, matches = match_topics(name, top_n=1, threshold=0.3)
    return matches[0][0] if matches else None


def bfs_prerequisites(goal):
    visited = {goal}
    queue = deque([goal])
    order = []

    while queue:
        current = queue.popleft()
        for prereq in TOPIC_GRAPH[current]:
            if prereq not in visited:
                visited.add(prereq)
                order.append(prereq)
                queue.append(prereq)

    return order


def dfs_study_order(topic, visited, order):
    if topic in visited:
        return
    visited.add(topic)

    for prereq in TOPIC_GRAPH[topic]:
        dfs_study_order(prereq, visited, order)

    order.append(topic)


def hops_to_goal(goal):
    # BFS backwards from the goal, gives the number of topics between each topic and the goal
    hops = {goal: 0}
    queue = deque([goal])
    while queue:
        current = queue.popleft()
        for prereq in TOPIC_GRAPH[current]:
            if prereq not in hops:
                hops[prereq] = hops[current] + 1
                queue.append(prereq)
    return hops


def search_route(start_topic, goal_topic):
    # A* search: f = hours so far + estimated hours left
    hops = hops_to_goal(goal_topic)
    open_list = [(MIN_HOURS * hops[start_topic], 0, start_topic, [start_topic])]
    best_cost = {start_topic: 0}
    checked = 0

    while open_list:
        f, cost, topic, route = heapq.heappop(open_list)
        if topic == goal_topic:
            return route, cost, checked
        if cost > best_cost[topic]:
            continue
        checked += 1

        for nxt in UNLOCKS[topic]:
            if nxt not in hops:
                continue
            new_cost = cost + TOPICS[nxt]["hours"]
            if new_cost < best_cost.get(nxt, float("inf")):
                best_cost[nxt] = new_cost
                heapq.heappush(open_list, (new_cost + MIN_HOURS * hops[nxt], new_cost, nxt, route + [nxt]))

    return None, None, checked


def fastest_route(start, goal):
    start_topic = find_topic(start) if start and start.strip() else None
    goal_topic = find_topic(goal) if goal and goal.strip() else None
    if not start_topic or not goal_topic:
        return {"status": "not_found", "message": "Start or goal topic not found."}

    if start_topic not in hops_to_goal(goal_topic):
        return {"status": "not_found",
                "message": f"{start_topic} does not lead to {goal_topic}, so there is no route."}

    # heuristic = (topics left) x (smallest topic hours)
    route, hours, checked = search_route(start_topic, goal_topic)

    return {
        "status": "success",
        "start": start_topic,
        "goal": goal_topic,
        "route": route,
        "hours_per_topic": [TOPICS[t]["hours"] for t in route[1:]],
        "total_hours": hours,
        "topics_checked": checked,
    }


def generate_learning_path(goal, known_topics=None, hours_per_week=None):
    if not goal or not goal.strip():
        return {"status": "error", "message": "Please enter what you want to learn."}

    known = set()
    for name in (known_topics or []):
        found = find_topic(name)
        if found:
            known.add(found)

    topic = find_topic(goal)

    if topic:
        order = []
        dfs_study_order(topic, set(known), order)
        prerequisites = bfs_prerequisites(topic)
        in_database = True
        message = ""
    else:
        topic = goal.strip()
        order = [topic]
        prerequisites = []
        in_database = False
        message = ("This topic is not in our topic graph (it only has computer science topics), "
                   "so its prerequisites are unknown. Here is a general plan with videos and links.")

    steps = []
    total_hours = 0
    for number, name in enumerate(order, start=1):
        step = get_topic_resources(name)
        if not in_database:
            step["subtopics"] = GENERAL_SUBTOPICS
        step["order"] = number
        step["prerequisites"] = TOPIC_GRAPH.get(name, [])
        total_hours += step["hours"] or 0
        step["cumulative_hours"] = total_hours
        steps.append(step)

    weeks = None
    if hours_per_week and hours_per_week > 0 and total_hours:
        weeks = -(-total_hours // hours_per_week)  # round up

    facts = {
        "in_database": in_database,
        "known_count": len(known),
        "steps": len(steps),
        "total_hours": total_hours,
        "hours_per_week": hours_per_week,
        "weeks": weeks,
        "has_advanced": any(step["level"] == "advanced" for step in steps),
    }

    expert = run_expert_system(facts)

    return {
        "status": "success",
        "goal": topic,
        "in_database": in_database,
        "message": message,
        "all_prerequisites": prerequisites,
        "learning_path": order,
        "total_hours": total_hours,
        "estimated_weeks": weeks,
        "advice": expert["advice"],
        "advice_details": expert["advice_details"],
        "rules_fired": expert["rules_fired"],
        "steps": steps,
    }


if __name__ == "__main__":
    goal = input("What do you want to learn? ")
    known = input("Topics you already know (comma separated, or press Enter): ")
    known_list = [t for t in known.split(",") if t.strip()]

    result = generate_learning_path(goal, known_list, hours_per_week=6)

    print("\nLearning Path Generator:")
    if result["status"] == "success":
        if result["message"]:
            print(result["message"])
        for step in result["steps"]:
            hours = f" (~{step['hours']} hours)" if step["hours"] else ""
            print(f"\n{step['order']}. {step['topic']}{hours}")
            for sub in step["subtopics"]:
                print(f"   * {sub}")
            for video in step["videos"]:
                print(f"   - Video: {video['title']}: {video['link']}")
            print("   - More videos:", step["search_links"]["youtube"])
        print(f"\nTotal: ~{result['total_hours']} hours "
              f"(about {result['estimated_weeks']} week(s) at 6 hours/week)")
        for tip in result["advice"]:
            print("Tip:", tip)
    else:
        print(result["message"])
