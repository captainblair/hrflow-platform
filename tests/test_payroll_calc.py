from datetime import date
from decimal import Decimal

import pytest

from app.services.payroll_calc import calculate_income_tax, calculate_payslip


@pytest.mark.parametrize(
    ("taxable", "expected"),
    [
        ("0", "0.00"),
        ("5000", "0.00"),
        ("5000.01", "0.00"),
        ("15000", "1000.00"),
        ("15000.01", "1000.00"),
        ("20000", "2000.00"),
    ],
)
def test_progressive_tax_boundaries(taxable, expected):
    assert calculate_income_tax(Decimal(taxable)) == Decimal(expected)


def test_zero_tax_salary_still_pays_social_security():
    result = calculate_payslip(
        monthly_salary=4500,
        start_date=date(2024, 1, 1),
        year=2026,
        month=7,
    )

    assert result["gross_pay"] == Decimal("4500.00")
    assert result["social_security"] == Decimal("225.00")
    assert result["income_tax"] == Decimal("0.00")
    assert result["net_pay"] == Decimal("4275.00")


def test_mid_month_joiner_is_prorated_by_calendar_days():
    result = calculate_payslip(
        monthly_salary=9000,
        start_date=date(2026, 7, 15),
        year=2026,
        month=7,
    )

    assert result["days_in_month"] == 31
    assert result["employed_days"] == 17
    assert result["eligible_days"] == 17
    assert result["gross_pay"] == Decimal("4935.48")


def test_approved_unpaid_leave_reduces_gross():
    result = calculate_payslip(
        monthly_salary=14000,
        start_date=date(2024, 1, 1),
        year=2026,
        month=7,
        unpaid_ranges=[(date(2026, 7, 10), date(2026, 7, 12))],
    )

    assert result["unpaid_leave_days"] == 3
    assert result["eligible_days"] == 28
    assert result["gross_pay"] == Decimal("12645.16")


def test_unpaid_leave_before_start_date_is_not_deducted():
    result = calculate_payslip(
        monthly_salary=9000,
        start_date=date(2026, 7, 15),
        year=2026,
        month=7,
        unpaid_ranges=[(date(2026, 7, 1), date(2026, 7, 5))],
    )

    assert result["unpaid_leave_days"] == 0
    assert result["eligible_days"] == 17
    assert result["gross_pay"] == Decimal("4935.48")


def test_full_month_unpaid_leave_produces_zero_pay():
    result = calculate_payslip(
        monthly_salary=14000,
        start_date=date(2024, 1, 1),
        year=2026,
        month=7,
        unpaid_ranges=[(date(2026, 7, 1), date(2026, 7, 31))],
    )

    assert result["gross_pay"] == Decimal("0.00")
    assert result["social_security"] == Decimal("0.00")
    assert result["income_tax"] == Decimal("0.00")
    assert result["net_pay"] == Decimal("0.00")
