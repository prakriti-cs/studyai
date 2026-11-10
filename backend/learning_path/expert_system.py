RULES = [
    {"name": "R1", "if": [("topic", "outside_cs")], "cf": 0.9,
     "then": ("advice", "Check your syllabus for the prerequisites of this topic.")},
    {"name": "R2", "if": [("knows", "nothing")], "cf": 0.8,
     "then": ("advice", "Tell us the topics you already know and we will skip them to save time.")},
    {"name": "R3", "if": [("prerequisites", "known")], "cf": 1.0,
     "then": ("advice", "You already know the prerequisites, so you can start this topic directly.")},
    {"name": "R4", "if": [("path", "long"), ("pace", "slow")], "cf": 0.9,
     "then": ("workload", "heavy")},
    {"name": "R5", "if": [("duration", "long"), ("difficulty", "advanced")], "cf": 0.7,
     "then": ("workload", "heavy")},
    {"name": "R6", "if": [("workload", "heavy")], "cf": 0.85,
     "then": ("advice", "This plan is heavy for your weekly hours, so split it into weekly milestones or study more hours.")},
    {"name": "R7", "if": [("workload", "heavy"), ("difficulty", "advanced")], "cf": 0.7,
     "then": ("advice", "Start the advanced topic early and ask your doubts often, because this plan is demanding.")},
    {"name": "R8", "if": [("path", "long")], "cf": 0.7,
     "then": ("advice", "This is a long path, so finish it stage by stage and revise after each topic.")},
    {"name": "R9", "if": [("difficulty", "advanced")], "cf": 0.8,
     "then": ("advice", "The path has advanced topics, so solve practice problems after watching the videos.")},
    {"name": "R10", "if": [("pace", "slow")], "cf": 0.8,
     "then": ("advice", "With under 5 hours a week, study a little every day instead of one long session.")},
    {"name": "R11", "if": [("pace", "fast")], "cf": 0.9,
     "then": ("advice", "With 15 or more hours a week, take a short break every hour.")},
    {"name": "R12", "if": [("duration", "long")], "cf": 0.8,
     "then": ("advice", "At this speed it takes more than 8 weeks, so try to raise your weekly hours.")},
]


def make_facts(info):
    facts = []
    if not info["in_database"]:
        facts.append(("topic", "outside_cs"))
    if info["in_database"] and info["known_count"] == 0:
        facts.append(("knows", "nothing"))
    if info["in_database"] and info["steps"] == 1:
        facts.append(("prerequisites", "known"))
    if info["total_hours"] > 30:
        facts.append(("path", "long"))
    if info["has_advanced"]:
        facts.append(("difficulty", "advanced"))
    if info["weeks"] is not None and info["weeks"] > 8:
        facts.append(("duration", "long"))

    hours = info["hours_per_week"]
    if hours is not None and hours < 5:
        facts.append(("pace", "slow"))
    elif hours is not None and hours >= 15:
        facts.append(("pace", "fast"))
    return facts


def combine(old, new):
    # two rules gave the same conclusion, the certainty goes up (the MYCIN way)
    return old + new * (1 - old)


def run_expert_system(info):
    facts = {fact: 1.0 for fact in make_facts(info)}
    fired = []

    changed = True
    while changed:
        changed = False
        for rule in RULES:
            if rule["name"] in fired or not all(c in facts for c in rule["if"]):
                continue

            cf = rule["cf"] * min(facts[c] for c in rule["if"])
            conclusion = rule["then"]
            facts[conclusion] = combine(facts[conclusion], cf) if conclusion in facts else cf
            fired.append(rule["name"])
            changed = True

    advice = [(cf, fact[1]) for fact, cf in facts.items() if fact[0] == "advice"]
    advice.sort(reverse=True)
    return {
        "advice": [text for cf, text in advice],
        "advice_details": [{"advice": text, "certainty": round(cf, 2)} for cf, text in advice],
        "rules_fired": fired,
    }
