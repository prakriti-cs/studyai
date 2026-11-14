# AI Study Planner — Three AI planning features

These modules are designed for the public `prakriti-cs/studyai` Flask backend as inspected on 15 November 2026. They use only Python's standard library in the new AI logic; Flask is already a backend dependency.

## Install into existing repository

Copy the `backend/` contents in this archive into your repository's `backend/`, preserving the existing files. Do not overwrite your existing `backend/app.py`.

In existing `backend/app.py`, add these two lines **after** `app = Flask(__name__)`:

```python
from backend.planning_routes import planning_api
app.register_blueprint(planning_api)
```

The new endpoints are:

- `POST /api/deadlines` — `{"assignments":[{"name":"AI project","deadline":"2026-11-16","estimated_hours":6}],"available_hours_per_day":2}`
- `POST /api/focus` — `{"fatigue":8,"workload":7}`
- `POST /api/goals` — `{"goal":"Complete AI","total_topics":20,"completed_topics":8,"days_left":5,"hours_per_day":2}`

## Run & test from repository root

```bash
python3 -m unittest discover -s tests -p 'test_planning_features.py' -v
python3 -m backend.deadline_manager.deadline_manager
python3 -m backend.focus_optimizer.focus_optimizer
python3 -m backend.goal_tracker.goal_tracker
python3 backend/app.py
```

To try the focus endpoint in another terminal:

```bash
curl -X POST http://127.0.0.1:5000/api/focus -H 'Content-Type: application/json' -d '{"fatigue":8,"workload":7}'
```

## Safe team collaboration

```bash
git switch -c feature/ai-planning-tools
git add backend/deadline_manager backend/focus_optimizer backend/goal_tracker backend/planning_routes.py tests/test_planning_features.py
git add backend/app.py
git commit -m 'Add rule-based deadline manager, fuzzy focus optimizer, expert goal tracker'
git push -u origin feature/ai-planning-tools
```

Then create a pull request into `main`. `backend/app.py` should be edited only with the two lines above, to avoid replacing teammates' code.

All recommendations are advisory and generated without persisting private student details.
