from datetime import date, datetime, timedelta

import pytest

from app.extensions import db
from app.models import LeaveRequest
from app.services.leave_rules import (
    business_days_between,
    is_overdue,
    validate_no_overlap,
    validate_notice,
    validate_team_coverage,
)
from app.utils.errors import ApiError


def test_annual_leave_requires_three_days_notice():
    today = date(2026, 7, 26)

    with pytest.raises(ApiError, match="at least 3 calendar days"):
        validate_notice("annual", today + timedelta(days=2), today=today)

    validate_notice("annual", today + timedelta(days=3), today=today)


def test_sick_leave_is_exempt_from_notice():
    today = date(2026, 7, 26)
    validate_notice("sick", today, today=today)


def test_pending_or_approved_overlap_is_blocked(employee_factory):
    employee = employee_factory("Alice")
    existing = LeaveRequest(
        employee_id=employee.id,
        leave_type="annual",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 12),
        status="pending",
    )
    db.session.add(existing)
    db.session.commit()

    with pytest.raises(ApiError, match="Overlaps existing pending leave"):
        validate_no_overlap(
            employee.id,
            start_date=date(2026, 8, 12),
            end_date=date(2026, 8, 15),
        )


def test_rejected_leave_does_not_block_new_request(employee_factory):
    employee = employee_factory("Alice")
    db.session.add(
        LeaveRequest(
            employee_id=employee.id,
            leave_type="annual",
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 12),
            status="rejected",
        )
    )
    db.session.commit()

    validate_no_overlap(
        employee.id,
        start_date=date(2026, 8, 11),
        end_date=date(2026, 8, 13),
    )


def test_team_coverage_blocks_second_person_away(employee_factory):
    first = employee_factory("Alice")
    second = employee_factory("Brian")
    employee_factory("Carol")
    day = date(2026, 8, 10)
    db.session.add(
        LeaveRequest(
            employee_id=first.id,
            leave_type="annual",
            start_date=day,
            end_date=day,
            status="approved",
        )
    )
    db.session.commit()

    with pytest.raises(ApiError, match="Team coverage too low"):
        validate_team_coverage(second, day, day)


def test_single_person_team_is_not_blocked(employee_factory):
    employee = employee_factory("Solo", team="Finance")
    day = date(2026, 8, 10)
    validate_team_coverage(employee, day, day)


def test_overdue_after_more_than_five_business_days(employee_factory):
    employee = employee_factory("Alice")
    leave = LeaveRequest(
        employee_id=employee.id,
        leave_type="annual",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 12),
        status="pending",
        created_at=datetime(2026, 7, 20, 9, 0),
    )
    db.session.add(leave)
    db.session.commit()

    assert business_days_between(date(2026, 7, 20), date(2026, 7, 27)) == 5
    assert is_overdue(leave, today=date(2026, 7, 27)) is False
    assert is_overdue(leave, today=date(2026, 7, 28)) is True


def test_decided_request_is_never_overdue(employee_factory):
    employee = employee_factory("Alice")
    leave = LeaveRequest(
        employee_id=employee.id,
        leave_type="annual",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 12),
        status="approved",
        created_at=datetime(2026, 7, 1, 9, 0),
    )

    assert is_overdue(leave, today=date(2026, 7, 28)) is False
