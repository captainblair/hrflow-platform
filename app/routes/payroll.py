from flask import Blueprint, jsonify, request

from app.schemas import serialize_payroll_period, serialize_payslip
from app.services import payroll_service
from app.utils.errors import ApiError

payroll_bp = Blueprint("payroll", __name__)


@payroll_bp.post("/preview")
def preview_payslip():
    """Calculate a payslip without saving it."""
    data = request.get_json(silent=True) or {}
    missing = [f for f in ("employee_id", "year", "month") if data.get(f) in (None, "")]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}")

    result = payroll_service.preview_employee_payslip(
        employee_id=int(data["employee_id"]),
        year=int(data["year"]),
        month=int(data["month"]),
    )
    return jsonify(result)


@payroll_bp.post("/generate")
def generate_payroll():
    data = request.get_json(silent=True) or {}
    missing = [f for f in ("year", "month") if data.get(f) in (None, "")]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}")

    period, payslips = payroll_service.generate_payroll(
        year=int(data["year"]),
        month=int(data["month"]),
    )
    return (
        jsonify(
            {
                "period": serialize_payroll_period(period),
                "payslip_count": len(payslips),
                "payslips": [serialize_payslip(item) for item in payslips],
            }
        ),
        201,
    )


@payroll_bp.get("/periods")
def list_periods():
    periods = payroll_service.list_periods()
    return jsonify([serialize_payroll_period(item) for item in periods])


@payroll_bp.get("/periods/<int:period_id>/payslips")
def period_payslips(period_id):
    payslips = payroll_service.list_payslips_for_period(period_id)
    return jsonify([serialize_payslip(item) for item in payslips])


@payroll_bp.post("/periods/<int:period_id>/finalize")
def finalize_period(period_id):
    period = payroll_service.finalize_period(period_id)
    return jsonify(serialize_payroll_period(period))


@payroll_bp.get("/payslips/<int:payslip_id>")
def get_payslip(payslip_id):
    payslip = payroll_service.get_payslip(payslip_id)
    return jsonify(serialize_payslip(payslip))
