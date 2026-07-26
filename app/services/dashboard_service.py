from datetime import date, timedelta

from app.models import Employee, LeaveBalance, LeaveRequest, PayrollPeriod, Payslip
from app.schemas import (
    serialize_leave_balance,
    serialize_leave_request,
    serialize_payroll_period,
    serialize_payslip,
)
from app.services.leave_rules import is_overdue


def _covers(leave, day):
    return leave.start_date <= day <= leave.end_date


def get_dashboard():
    today = date.today()
    window_end = today + timedelta(days=14)
    year = today.year

    employees = Employee.query.order_by(Employee.name).all()
    active = [e for e in employees if e.is_active]

    leave_requests = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
    pending = [item for item in leave_requests if item.status == "pending"]
    overdue = [item for item in pending if is_overdue(item)]

    out_today = [
        item
        for item in leave_requests
        if item.status == "approved" and _covers(item, today)
    ]
    # One row per person if they somehow have overlapping approved leave.
    seen = set()
    out_today_unique = []
    for item in out_today:
        if item.employee_id in seen:
            continue
        seen.add(item.employee_id)
        out_today_unique.append(item)

    upcoming = [
        item
        for item in leave_requests
        if item.status == "approved"
        and item.end_date >= today
        and item.start_date <= window_end
    ]
    upcoming.sort(key=lambda item: item.start_date)

    balances = (
        LeaveBalance.query.join(Employee)
        .filter(LeaveBalance.year == year, Employee.is_active.is_(True))
        .order_by(Employee.name)
        .all()
    )

    periods = PayrollPeriod.query.order_by(
        PayrollPeriod.year.desc(), PayrollPeriod.month.desc()
    ).all()
    latest_period = periods[0] if periods else None
    recent_payslips = []
    if latest_period:
        recent_payslips = (
            Payslip.query.filter_by(period_id=latest_period.id)
            .order_by(Payslip.employee_id)
            .limit(8)
            .all()
        )

    return {
        "as_of": today.isoformat(),
        "summary": {
            "total_employees": len(employees),
            "active_employees": len(active),
            "inactive_employees": len(employees) - len(active),
            "employees_on_leave_today": len(out_today_unique),
            "pending_leave_requests": len(pending),
            "overdue_leave_requests": len(overdue),
            "payroll_periods": len(periods),
            "latest_period": (
                f"{latest_period.year}-{latest_period.month:02d}"
                if latest_period
                else None
            ),
            "latest_payslip_count": (
                len(latest_period.payslips) if latest_period else 0
            ),
        },
        "pending_approvals": [serialize_leave_request(item) for item in pending[:10]],
        "out_today": [serialize_leave_request(item) for item in out_today_unique],
        "upcoming_leave": [serialize_leave_request(item) for item in upcoming[:10]],
        "recent_leave": [serialize_leave_request(item) for item in leave_requests[:8]],
        "leave_balances": [serialize_leave_balance(item) for item in balances],
        "payroll_periods": [serialize_payroll_period(item) for item in periods[:5]],
        "recent_payslips": [serialize_payslip(item) for item in recent_payslips],
    }
