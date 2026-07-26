from flask import Blueprint, jsonify, request

from app.schemas import serialize_leave_balance, serialize_leave_request
from app.services import leave_service
from app.utils.errors import ApiError

leave_bp = Blueprint("leave", __name__)


@leave_bp.get("")
def list_leave():
    status = request.args.get("status")
    employee_id = request.args.get("employee_id", type=int)
    overdue = request.args.get("overdue", "").lower() in ("1", "true", "yes")
    requests = leave_service.list_leave_requests(
        status=status, employee_id=employee_id, overdue_only=overdue
    )
    return jsonify([serialize_leave_request(item) for item in requests])


@leave_bp.post("")
def submit_leave():
    data = request.get_json(silent=True) or {}
    leave = leave_service.submit_leave(data)
    return jsonify(serialize_leave_request(leave)), 201


@leave_bp.get("/coverage")
def coverage():
    raw_date = request.args.get("date")
    if not raw_date:
        raise ApiError("date query parameter is required (YYYY-MM-DD)")
    try:
        from datetime import date

        day = date.fromisoformat(raw_date)
    except ValueError:
        raise ApiError("date must be an ISO date (YYYY-MM-DD)")

    team = request.args.get("team")
    return jsonify(leave_service.get_coverage(day, team=team))


@leave_bp.get("/balances/<int:employee_id>")
def get_balance(employee_id):
    year = request.args.get("year", type=int)
    balance = leave_service.get_balance(employee_id, year=year)
    return jsonify(serialize_leave_balance(balance))


@leave_bp.post("/<int:leave_id>/approve")
def approve_leave(leave_id):
    data = request.get_json(silent=True) or {}
    leave = leave_service.approve_leave(leave_id, data)
    return jsonify(serialize_leave_request(leave))


@leave_bp.post("/<int:leave_id>/reject")
def reject_leave(leave_id):
    data = request.get_json(silent=True) or {}
    leave = leave_service.reject_leave(leave_id, data)
    return jsonify(serialize_leave_request(leave))
