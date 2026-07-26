from datetime import date, datetime, timedelta

from app.models import Employee, LeaveRequest
from app.utils.errors import ApiError

MIN_NOTICE_DAYS = 3
OVERDUE_BUSINESS_DAYS = 5
# Soft cap: for teams with 2+ active people, at most half may be away.
COVERAGE_TEAM_MIN_SIZE = 2


def business_days_between(start, end):
    """Count weekdays from start (exclusive) up to end (inclusive).

    Used for overdue: how many business days have passed since the request
    was created.
    """
    if end <= start:
        return 0
    days = 0
    cursor = start + timedelta(days=1)
    while cursor <= end:
        if cursor.weekday() < 5:
            days += 1
        cursor += timedelta(days=1)
    return days


def is_overdue(leave, today=None):
    if leave.status != "pending" or leave.created_at is None:
        return False
    today = today or date.today()
    created = leave.created_at.date() if isinstance(leave.created_at, datetime) else leave.created_at
    return business_days_between(created, today) > OVERDUE_BUSINESS_DAYS


def validate_notice(leave_type, start_date, today=None):
    # Sick leave is exempt — people usually cannot give advance notice.
    if leave_type != "annual":
        return
    today = today or date.today()
    notice = (start_date - today).days
    if notice < MIN_NOTICE_DAYS:
        raise ApiError(
            f"Annual leave needs at least {MIN_NOTICE_DAYS} calendar days notice "
            f"({notice} given)"
        )


def dates_overlap(start_a, end_a, start_b, end_b):
    return start_a <= end_b and start_b <= end_a


def validate_no_overlap(employee_id, start_date, end_date, exclude_leave_id=None):
    query = LeaveRequest.query.filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status.in_(("pending", "approved")),
    )
    if exclude_leave_id is not None:
        query = query.filter(LeaveRequest.id != exclude_leave_id)

    for existing in query.all():
        if dates_overlap(start_date, end_date, existing.start_date, existing.end_date):
            raise ApiError(
                f"Overlaps existing {existing.status} leave "
                f"({existing.start_date.isoformat()} to {existing.end_date.isoformat()})"
            )


def _active_team_members(team):
    return Employee.query.filter_by(team=team, is_active=True).all()


def _people_away_on_date(team, day, exclude_employee_id=None, exclude_leave_id=None):
    """Active team members with pending/approved leave covering `day`."""
    members = {m.id: m for m in _active_team_members(team)}
    away = set()

    query = LeaveRequest.query.filter(
        LeaveRequest.status.in_(("pending", "approved")),
        LeaveRequest.start_date <= day,
        LeaveRequest.end_date >= day,
    )
    if exclude_leave_id is not None:
        query = query.filter(LeaveRequest.id != exclude_leave_id)

    for leave in query.all():
        if leave.employee_id not in members:
            continue
        if exclude_employee_id is not None and leave.employee_id == exclude_employee_id:
            continue
        away.add(leave.employee_id)
    return away


def max_away_allowed(active_count):
    if active_count < COVERAGE_TEAM_MIN_SIZE:
        return active_count
    return active_count // 2


def validate_team_coverage(employee, start_date, end_date, exclude_leave_id=None):
    members = _active_team_members(employee.team)
    active_count = len(members)
    if active_count < COVERAGE_TEAM_MIN_SIZE:
        return

    limit = max_away_allowed(active_count)
    day = start_date
    while day <= end_date:
        away = _people_away_on_date(
            employee.team,
            day,
            exclude_employee_id=employee.id,
            exclude_leave_id=exclude_leave_id,
        )
        # Include this employee in the projected headcount for the day.
        projected = len(away) + 1
        if projected > limit:
            raise ApiError(
                f"Team coverage too low on {day.isoformat()}: "
                f"{projected}/{active_count} of {employee.team} would be away "
                f"(max {limit})"
            )
        day += timedelta(days=1)


def coverage_for_date(day, team=None):
    query = Employee.query.filter_by(is_active=True)
    if team:
        query = query.filter_by(team=team)
    employees = query.order_by(Employee.team, Employee.name).all()

    teams = {}
    for employee in employees:
        teams.setdefault(employee.team, []).append(employee)

    result = []
    for team_name, members in teams.items():
        active_count = len(members)
        away_ids = _people_away_on_date(team_name, day)
        away_people = [
            {"id": m.id, "name": m.name, "role": m.role}
            for m in members
            if m.id in away_ids
        ]
        result.append(
            {
                "team": team_name,
                "date": day.isoformat(),
                "active_count": active_count,
                "away_count": len(away_people),
                "max_away": max_away_allowed(active_count),
                "over_limit": len(away_people) > max_away_allowed(active_count),
                "away": away_people,
            }
        )
    return result
