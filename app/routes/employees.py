from flask import Blueprint, jsonify, request

from app.schemas import serialize_employee
from app.services import employee_service

employees_bp = Blueprint("employees", __name__)


def _parse_active_filter():
    value = request.args.get("active")
    if value is None:
        return None
    return value.lower() in ("1", "true", "yes")


@employees_bp.get("")
def list_employees():
    active = _parse_active_filter()
    team = request.args.get("team")
    employees = employee_service.list_employees(active=active, team=team)
    return jsonify([serialize_employee(e) for e in employees])


@employees_bp.post("")
def create_employee():
    data = request.get_json(silent=True) or {}
    employee = employee_service.create_employee(data)
    return jsonify(serialize_employee(employee)), 201


@employees_bp.get("/org")
def org_tree():
    return jsonify(employee_service.build_org_tree())


@employees_bp.get("/<int:employee_id>")
def get_employee(employee_id):
    employee = employee_service.get_employee(employee_id)
    return jsonify(serialize_employee(employee))


@employees_bp.patch("/<int:employee_id>")
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}
    employee = employee_service.update_employee(employee_id, data)
    return jsonify(serialize_employee(employee))


@employees_bp.post("/<int:employee_id>/deactivate")
def deactivate_employee(employee_id):
    employee = employee_service.deactivate_employee(employee_id)
    return jsonify(serialize_employee(employee))
