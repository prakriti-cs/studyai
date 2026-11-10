import os
import sys

# so that "shared" and "backend" can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request

from backend.doubt_assistant.doubt_assistant import answer_doubt
from backend.resource_recommender.resource_recommender import recommend_resources
from backend.learning_path.learning_path import generate_learning_path, fastest_route

app = Flask(__name__)


@app.after_request
def allow_frontend(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def get_input():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else request.args.to_dict()


def to_number(value, default=None, kind=int):
    try:
        return kind(value)
    except (TypeError, ValueError):
        return default


def to_list(value):
    if isinstance(value, list):
        return value
    return [item.strip() for item in (value or "").split(",") if item.strip()]


@app.route("/")
def home():
    return jsonify({
        "message": "AI Study Planner backend is running.",
        "try_in_browser": {
            "doubt": "/api/doubt?question=what is bfs",
            "recommend": "/api/recommend?query=graph traversal",
            "learning_path": "/api/learning-path?goal=BFS&known_topics=Arrays&hours_per_week=6",
            "route": "/api/route?start=Arrays&goal=BFS",
        },
        "note": "Each endpoint also accepts a POST request with a JSON body.",
    })


@app.route("/api/doubt", methods=["GET", "POST"])
def doubt():
    data = get_input()
    return jsonify(answer_doubt(data.get("question", ""), data.get("subject")))


@app.route("/api/recommend", methods=["GET", "POST"])
def recommend():
    data = get_input()
    return jsonify(recommend_resources(
        data.get("query", ""),
        level=data.get("level"),
        top_n=to_number(data.get("top_n"), 3),
    ))


@app.route("/api/learning-path", methods=["GET", "POST"])
def learning_path():
    data = get_input()
    return jsonify(generate_learning_path(
        data.get("goal", ""),
        to_list(data.get("known_topics")),
        hours_per_week=to_number(data.get("hours_per_week"), None, float),
    ))


@app.route("/api/route", methods=["GET", "POST"])
def route():
    data = get_input()
    return jsonify(fastest_route(data.get("start", ""), data.get("goal", "")))


if __name__ == "__main__":
    app.run(debug=True)
