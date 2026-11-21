from collections import defaultdict, deque

class SyllabusKnowledgeBase:
    """Knowledge representation: subjects, topics and prerequisite facts."""
    def __init__(self, subjects):
        self.subjects = subjects
        self.topics = {}
        self.prerequisites = defaultdict(list)
        self.topic_subject = {}
        for subject in subjects:
            for topic in subject.get("topics", []):
                name = topic["name"]
                if name in self.topics:
                    raise ValueError(f"Duplicate topic: {name}")
                difficulty = float(topic.get("difficulty", 3))
                importance = float(topic.get("importance", 3))
                hours = float(topic.get("estimated_hours", 1))
                if not 1 <= difficulty <= 5 or not 1 <= importance <= 5 or hours <= 0:
                    raise ValueError(f"Invalid difficulty, importance or hours for {name}")
                self.topics[name] = {
                    "name": name, "difficulty": difficulty, "importance": importance,
                    "estimated_hours": hours, "subject": subject["name"]
                }
                self.topic_subject[name] = subject["name"]
                self.prerequisites[name] = list(topic.get("prerequisites", []))

        for topic, required in self.prerequisites.items():
            for prerequisite in required:
                if prerequisite not in self.topics:
                    raise ValueError(f"Unknown prerequisite '{prerequisite}' for '{topic}'")
                if prerequisite == topic:
                    raise ValueError(f"'{topic}' cannot be its own prerequisite")
        self.learning_order()  # Detect circular dependencies.

    def learning_order(self):
        indegree = {name: len(self.prerequisites[name]) for name in self.topics}
        dependents = defaultdict(list)
        for topic, required in self.prerequisites.items():
            for prerequisite in required:
                dependents[prerequisite].append(topic)
        queue = deque(name for name, degree in indegree.items() if degree == 0)
        order = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for dependent in dependents[current]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)
        if len(order) != len(self.topics):
            raise ValueError("Circular prerequisite dependency detected")
        return order

    def analyze(self):
        return {
            "subjects": [
                {"name": s["name"], "units": s.get("units", []),
                 "topics": [t["name"] for t in s.get("topics", [])]}
                for s in self.subjects
            ],
            "topic_count": len(self.topics),
            "prerequisites": dict(self.prerequisites),
            "recommended_learning_order": self.learning_order()
        }
