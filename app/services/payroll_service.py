from decimal import Decimal

from app.models import Employee, LeaveRequest
from app.services.payroll_calc import calculate_payslip
from app.utils.errors import ApiError


def _unpaid_ranges_for_employee(employee_id):
    leaves = LeaveRequest.query.filter_by(
        employee_id=employee_id,
        leave_type="unpaid",
        status="approved",
    ).all()
    return [(leave.start_date, leave.end_date) for leave in leaves]


def preview_employee_payslip(employee_id, year, month):
    if month < 1 or month > 12:
        raise ApiError("month must be between 1 and 12")

    employee = Employee.query.get(employee_id)
    if employee is None:
        raise ApiError("Employee not found", status_code=404)
    if not employee.is_active:
        raise ApiError("Inactive employees are skipped for payroll")

    result = calculate_payslip(
        monthly_salary=employee.salary,
        start_date=employee.start_date,
        year=year,
        month=month,
        unpaid_ranges=_unpaid_ranges_for_employee(employee.id),
    )

    payload = {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "persisted": False,
    }
    for key, value in result.items():
        payload[key] = float(value) if isinstance(value, Decimal) else value
    return payload
