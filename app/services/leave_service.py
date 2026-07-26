from datetime import date, datetime

from app.extensions import db
from app.models import Employee, LeaveBalance, LeaveRequest
from app.models.leave import LEAVE_TYPES
from app.services import leave_rules
from app.utils.errors import ApiError


def _parse_date(value, field_name):
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ApiError(f"{field_name} must be an ISO date (YYYY-MM-DD)")


def leave_days(start_date, end_date):
    return (end_date - start_date).days + 1


def get_or_create_balance(employee_id, year=None):
    year = year or date.today().year
    balance = LeaveBalance.query.filter_by(employee_id=employee_id, year=year).first()
    if balance is None:
        balance = LeaveBalance(
            employee_id=employee_id,
            year=year,
            annual_allocated=21,
            annual_used=0,
        )
        db.session.add(balance)
        db.session.flush()
    return balance


def list_leave_requests(status=None, employee_id=None, overdue_only=False):
    query = LeaveRequest.query
    if status:
        query = query.filter_by(status=status)
    if employee_id is not None:
        query = query.filter_by(employee_id=employee_id)

    results = query.order_by(LeaveRequest.created_at.desc()).all()
    if overdue_only:
        results = [item for item in results if leave_rules.is_overdue(item)]
    return results


def get_leave_request(leave_id):
    leave = db.session.get(LeaveRequest, leave_id)
    if leave is None:
        raise ApiError("Leave request not found", status_code=404)
    return leave


def submit_leave(data):
    required = ("employee_id", "leave_type", "start_date", "end_date")
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}")

    employee = db.session.get(Employee, data["employee_id"])
    if employee is None:
        raise ApiError("Employee not found", status_code=404)
    if not employee.is_active:
        raise ApiError("Inactive employees cannot request leave")

    leave_type = data["leave_type"]
    if leave_type not in LEAVE_TYPES:
        raise ApiError(f"leave_type must be one of: {', '.join(LEAVE_TYPES)}")

    start_date = _parse_date(data["start_date"], "start_date")
    end_date = _parse_date(data["end_date"], "end_date")
    if end_date < start_date:
        raise ApiError("end_date cannot be before start_date")

    leave_rules.validate_notice(leave_type, start_date)
    leave_rules.validate_no_overlap(employee.id, start_date, end_date)
    leave_rules.validate_team_coverage(employee, start_date, end_date)

    leave = LeaveRequest(
        employee_id=employee.id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=(data.get("reason") or "").strip() or None,
        status="pending",
    )
    db.session.add(leave)
    db.session.commit()
    return leave


def _require_pending(leave):
    if leave.status != "pending":
        raise ApiError(f"Only pending requests can be decided (current: {leave.status})")


def _resolve_approver(leave, data):
    # No auth yet, so the caller must pass who is deciding. In a real system
    # this would come from the logged-in manager session.
    approver_id = data.get("approver_id")
    if approver_id is None:
        raise ApiError("approver_id is required")

    approver = db.session.get(Employee, approver_id)
    if approver is None:
        raise ApiError("Approver not found", status_code=404)
    if not approver.is_active:
        raise ApiError("Approver is inactive")

    if leave.employee.manager_id and approver.id != leave.employee.manager_id:
        raise ApiError("Only the employee's manager can decide this request")

    return approver


def approve_leave(leave_id, data):
    leave = get_leave_request(leave_id)
    _require_pending(leave)
    approver = _resolve_approver(leave, data)

    # Re-check coverage at decision time in case other leave landed since submit.
    leave_rules.validate_team_coverage(
        leave.employee,
        leave.start_date,
        leave.end_date,
        exclude_leave_id=leave.id,
    )

    days = leave_days(leave.start_date, leave.end_date)

    if leave.leave_type == "annual":
        balance = get_or_create_balance(leave.employee_id, leave.start_date.year)
        if balance.annual_remaining < days:
            raise ApiError(
                f"Insufficient annual leave balance "
                f"({balance.annual_remaining} remaining, {days} requested)"
            )
        balance.annual_used += days

    leave.status = "approved"
    leave.decided_at = datetime.now()
    leave.decided_by = approver.id
    db.session.commit()
    return leave


def reject_leave(leave_id, data):
    leave = get_leave_request(leave_id)
    _require_pending(leave)
    approver = _resolve_approver(leave, data)

    leave.status = "rejected"
    leave.decided_at = datetime.now()
    leave.decided_by = approver.id
    db.session.commit()
    return leave


def get_balance(employee_id, year=None):
    employee = db.session.get(Employee, employee_id)
    if employee is None:
        raise ApiError("Employee not found", status_code=404)
    year = year or date.today().year
    balance = get_or_create_balance(employee_id, year)
    db.session.commit()
    return balance


def get_coverage(day, team=None):
    return leave_rules.coverage_for_date(day, team=team)
