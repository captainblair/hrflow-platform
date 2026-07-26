from flask import Blueprint, jsonify, request

from app.services import payroll_service

payroll_bp = Blueprint("payroll", __name__)


@payroll_bp.post("/preview")
def preview_payslip():
    """Calculate a payslip without saving it. Persistence comes in the next phase."""
    data = request.get_json(silent=True) or {}
    employee_id = data.get("employee_id")
    year = data.get("year")
    month = data.get("month")

    missing = [f for f in ("employee_id", "year", "month") if data.get(f) in (None, "")]
    if missing:
        from app.utils.errors import ApiError

        raise ApiError(f"Missing required fields: {', '.join(missing)}")

    result = payroll_service.preview_employee_payslip(
        employee_id=int(employee_id),
        year=int(year),
        month=int(month),
    )
    return jsonify(result)
