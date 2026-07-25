from flask import Blueprint, jsonify, request

from app.schemas import serialize_leave_balance, serialize_leave_request
from app.services import leave_service

leave_bp = Blueprint("leave", __name__)


@leave_bp.get("")
def list_leave():
    status = request.args.get("status")
    employee_id = request.args.get("employee_id", type=int)
    requests = leave_service.list_leave_requests(
        status=status, employee_id=employee_id
    )
    return jsonify([serialize_leave_request(item) for item in requests])


@leave_bp.post("")
def submit_leave():
    data = request.get_json(silent=True) or {}
    leave = leave_service.submit_leave(data)
    return jsonify(serialize_leave_request(leave)), 201


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
