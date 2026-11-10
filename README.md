# AI Study Planner (AI backend)

```
AI-Study-Planner/
├── frontend/
├── backend/
│   ├── doubt_assistant/       doubt_assistant.py        answer_doubt(query, subject=None)
│   ├── resource_recommender/  resource_recommender.py   recommend_resources(query, level=None, top_n=3)
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
python backend/app.py
```

## How each module works

- **Doubt Assistant**: TF-IDF + cosine similarity on word pieces finds the closest entry in `KNOWLEDGE_BASE`. If nothing matches it looks the topic up on Wikipedia (needs internet), then falls back to `not_found` with a `did_you_mean` list. It also returns a fuzzy `confidence`.
- **Resource Recommender**: fixes spelling mistakes, matches the query to topics with TF-IDF + cosine similarity, and returns each topic's YouTube videos plus search links, with a fuzzy `confidence` for each match.
- **Learning Path Generator**: BFS and DFS build the prerequisite order, topics the student already knows are skipped, and every step has subtopics, hours and YouTube videos. The expert system adds `advice`.
- **Fastest route**: A\* finds the route with the fewest study hours between two topics.

## Responsible AI

- **Transparent:** answers show their similarity score and fuzzy confidence, answers that come from Wikipedia are labelled, and the expert system lists the rules it used.
- **No guessing:** below the match threshold the Doubt Assistant says `not_found` instead of inventing an answer.
- **Privacy:** nothing about the student is stored.
- **Limits:** the data is a small, hand-written sample (computer science only).
