# AI Study Planner (AI backend)

```
AI-Study-Planner/
├── frontend/
├── backend/
│   ├── doubt_assistant/       doubt_assistant.py        answer_doubt(query, subject=None)
│   ├── resource_recommender/  resource_recommender.py   recommend_resources(query, level=None, top_n=3)
│   ├── revision_scheduler/    revision_scheduler.py     build_revision_schedule(topics, ...)   beam search
│   ├── readiness_evaluator/   readiness_evaluator.py    evaluate_readiness(topics, ...)        Bayesian + Monte Carlo
│   ├── time_allocator/        time_allocator.py         allocate_study_time(topics, ...)       expected utility
│   ├── learning_path/
│   │   ├── learning_path.py   generate_learning_path(goal, known_topics=None, hours_per_week=None), fastest_route(start, goal)
│   │   └── expert_system.py   rules + inference engine + certainty factors
│   ├── app.py                 Flask API
│   └── requirements.txt
├── shared/
│   ├── common/
│   │   ├── text_utils.py      preprocess, TF-IDF + cosine similarity
│   │   ├── fuzzy.py           fuzzy low / medium / high confidence
│   │   ├── topic_search.py    spelling correction, topic matching, YouTube/Google/Wikipedia links
│   │   └── web_lookup.py      Wikipedia lookup used by the Doubt Assistant
│   └── database/
│       └── topics_data.py     all topics: prerequisites, keywords, hours, subtopics, YouTube videos
└── README.md
```

## Setup and run (from the AI-Study-Planner folder)

```
pip install -r backend/requirements.txt
python -m backend.doubt_assistant.doubt_assistant
python -m backend.resource_recommender.resource_recommender
python -m backend.learning_path.learning_path
python -m backend.revision_scheduler.revision_scheduler
python -m backend.readiness_evaluator.readiness_evaluator
python -m backend.time_allocator.time_allocator
python backend/app.py
```

## How each module works

- **Doubt Assistant**: TF-IDF + cosine similarity on word pieces finds the closest entry in `KNOWLEDGE_BASE`. If nothing matches it looks the topic up on Wikipedia (needs internet), then falls back to `not_found` with a `did_you_mean` list. It also returns a fuzzy `confidence`.
- **Resource Recommender**: fixes spelling mistakes, matches the query to topics with TF-IDF + cosine similarity, and returns each topic's YouTube videos plus search links, with a fuzzy `confidence` for each match.
- **Learning Path Generator**: BFS and DFS build the prerequisite order, topics the student already knows are skipped, and every step has subtopics, hours and YouTube videos. The expert system adds `advice`.
- **Fastest route**: A\* finds the route with the fewest study hours between two topics.
- **Revision Scheduler** (`POST /api/revision-schedule`): each topic decays on an exponential forgetting curve, and beam search chooses the best set of topics for every day within a daily minute budget. Sessions show retention before review, minutes and the resulting mastery; the response reports the search width, states expanded and final retention per topic.
- **Exam Readiness Evaluator** (`POST /api/readiness`): mastery is a Beta belief per topic, prerequisites dampen dependent topics, and Monte Carlo simulation gives the probability of passing, a 5-95% credible score range and the three highest-leverage topics to improve next. A shared `exam_noise` paper-difficulty factor keeps the probability graded near the pass mark instead of collapsing to 0 or 1 on exams with many topics.
- **Study Time Allocator** (`POST /api/allocate-time`): blocks of time are assigned by greedy marginal expected utility with diminishing returns, so time moves to the topic with the best expected grade gain per block. The response logs each decision with the runner-up it beat and leaves time unallocated when study would add nothing.

### Example request bodies

```json
POST /api/revision-schedule
{"start_date":"2026-11-15","days":5,"minutes_per_day":90,
 "topics":[{"name":"Graphs","mastery":0.4,"difficulty":4,"exam_weight":2,"last_studied":"2026-11-02"}]}

POST /api/readiness
{"pass_mark":0.6,
 "topics":[{"name":"Arrays","mastery":0.7,"exam_weight":2},
           {"name":"Trees","mastery":0.4,"exam_weight":3,"prerequisites":["Arrays"]}]}

POST /api/allocate-time
{"available_hours":4,"block_minutes":30,
 "topics":[{"name":"DP","mastery":0.3,"exam_weight":4,"learning_rate":0.5}]}
```

## Tune to a real syllabus (DBMS example)

`backend/exam_profiles/dbms.py` holds a DBMS syllabus profile: 18 topics across the four units, exam weights derived from unit teaching hours, prerequisite links (data models -> ER -> relational -> algebra/SQL -> dependencies -> normalisation), and assumed mastery values. It runs all three planners and prints a ready-to-use plan:

```bash
python3 -m backend.exam_profiles.dbms
python3 -m backend.exam_profiles.dbms --days 10 --hours-per-day 3 --pass-mark 0.45
python3 -m backend.exam_profiles.dbms --mastery "Relational Algebra=0.7" "Normalization (1NF to 5NF)=0.55"
```

Recommended defaults for a 42-hour theory paper: `pass_mark=0.40` (the usual pass mark, with 0.50/0.60/0.70 printed as safer targets), `confidence=0.50`, `exam_noise=0.07`, `target_retention=0.75`, 30-minute allocation blocks, `risk_aversion=0.35` and a 3-hour per-topic cap. Override assumed mastery with `--mastery`; nothing is stored or sent anywhere.

Note that the readiness score and the allocator's expected score differ slightly: readiness applies the prerequisite penalties, while the allocator treats topics as independent so it can attribute marginal gains per block.

## Responsible AI

- **Transparent:** answers show their similarity score and fuzzy confidence, answers that come from Wikipedia are labelled, and the expert system lists the rules it used. The new planners also explain themselves: the scheduler reports its search statistics, the readiness evaluator lists its probability assumptions and per-topic contributions, and the allocator logs the marginal utility behind every decision.
- **Advisory, not certain:** readiness is a probability under stated assumptions, not a promise; the allocator and scheduler recommend a plan but never lock a student into it.
- **No guessing:** below the match threshold the Doubt Assistant says `not_found` instead of inventing an answer.
- **Privacy:** nothing about the student is stored.
- **Limits:** the data is a small, hand-written sample (computer science only).
