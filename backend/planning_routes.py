"""Drop-in Flask Blueprint for three AI Study Planner features."""
from flask import Blueprint, jsonify, request
from backend.deadline_manager.deadline_manager import manage_deadlines
from backend.focus_optimizer.focus_optimizer import optimize_break
from backend.goal_tracker.goal_tracker import track_goal
from backend.revision_scheduler.revision_scheduler import build_revision_schedule
from backend.readiness_evaluator.readiness_evaluator import evaluate_readiness
from backend.time_allocator.time_allocator import allocate_study_time

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


@planning_api.route('/api/revision-schedule', methods=['POST'])
def revision_schedule():
    return handle(lambda p: build_revision_schedule(
        p['topics'], start_date=p.get('start_date'), days=p.get('days', 7),
        minutes_per_day=p.get('minutes_per_day', 60), beam_width=p.get('beam_width', 5),
        target_retention=p.get('target_retention', 0.7)))


@planning_api.route('/api/readiness', methods=['POST'])
def readiness():
    return handle(lambda p: evaluate_readiness(
        p['topics'], pass_mark=p.get('pass_mark', 0.5), confidence=p.get('confidence'),
        simulations=p.get('simulations', 2000), seed=p.get('seed', 7),
        exam_noise=p.get('exam_noise', 0.07), improvement=p.get('improvement', 0.2)))


@planning_api.route('/api/allocate-time', methods=['POST'])
def allocate_time():
    return handle(lambda p: allocate_study_time(
        p['topics'], p['available_hours'], block_minutes=p.get('block_minutes', 15),
        risk_aversion=p.get('risk_aversion', 0.3),
        max_hours_per_topic=p.get('max_hours_per_topic')))
