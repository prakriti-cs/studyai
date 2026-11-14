"""Drop-in Flask Blueprint for three AI Study Planner features."""
from flask import Blueprint, jsonify, request
from backend.deadline_manager.deadline_manager import manage_deadlines
from backend.focus_optimizer.focus_optimizer import optimize_break
from backend.goal_tracker.goal_tracker import track_goal

planning_api = Blueprint('planning_api', __name__)


def handle(callback):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({'error': 'Expected a JSON object'}), 400
    try:
        return jsonify(callback(payload))
    except (ValueError, KeyError, TypeError) as exc:
        return jsonify({'error': str(exc)}), 400


@planning_api.route('/api/deadlines', methods=['POST'])
def deadlines():
    return handle(lambda p: manage_deadlines(p['assignments'],
                     available_hours_per_day=p.get('available_hours_per_day', 2)))


@planning_api.route('/api/focus', methods=['POST'])
def focus():
    return handle(lambda p: optimize_break(p['fatigue'], p['workload']))


@planning_api.route('/api/goals', methods=['POST'])
def goals():
    return handle(lambda p: track_goal(p['goal'], p['total_topics'], p['completed_topics'],
                    p['days_left'], p.get('hours_per_day', 2), p.get('hours_per_topic', 1)))
