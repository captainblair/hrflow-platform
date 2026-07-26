from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


SOCIAL_SECURITY_RATE = Decimal("0.05")
TAX_BAND_1 = Decimal("5000")
TAX_BAND_2 = Decimal("15000")
TAX_RATE_MID = Decimal("0.10")
TAX_RATE_HIGH = Decimal("0.20")


def money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def days_in_month(year, month):
    return monthrange(year, month)[1]


def month_bounds(year, month):
    last = days_in_month(year, month)
    return date(year, month, 1), date(year, month, last)


def count_overlap_days(range_start, range_end, window_start, window_end):
    start = max(range_start, window_start)
    end = min(range_end, window_end)
    if end < start:
        return 0
    return (end - start).days + 1


def employed_days_in_month(start_date, year, month):
    """Calendar days the person was employed during the pay month."""
    month_start, month_end = month_bounds(year, month)
    if start_date > month_end:
        return 0
    employed_from = max(start_date, month_start)
    return (month_end - employed_from).days + 1


def unpaid_leave_days_in_month(leave_ranges, year, month, employment_start=None):
    """Sum approved unpaid leave days inside the employee's paid window."""
    month_start, month_end = month_bounds(year, month)
    window_start = max(month_start, employment_start) if employment_start else month_start
    if window_start > month_end:
        return 0

    total = 0
    for leave_start, leave_end in leave_ranges:
        total += count_overlap_days(leave_start, leave_end, window_start, month_end)
    return total


def calculate_gross(monthly_salary, eligible_days, days_in_period):
    if days_in_period <= 0 or eligible_days <= 0:
        return money(0)
    salary = Decimal(str(monthly_salary))
    return money(salary * Decimal(eligible_days) / Decimal(days_in_period))


def calculate_social_security(gross):
    return money(Decimal(str(gross)) * SOCIAL_SECURITY_RATE)


def calculate_income_tax(taxable):
    """Progressive brackets on taxable income (gross - social security)."""
    taxable = Decimal(str(taxable))
    if taxable <= 0:
        return money(0)
    if taxable <= TAX_BAND_1:
        return money(0)
    if taxable <= TAX_BAND_2:
        return money((taxable - TAX_BAND_1) * TAX_RATE_MID)

    mid_portion = (TAX_BAND_2 - TAX_BAND_1) * TAX_RATE_MID
    high_portion = (taxable - TAX_BAND_2) * TAX_RATE_HIGH
    return money(mid_portion + high_portion)


def calculate_payslip(monthly_salary, start_date, year, month, unpaid_ranges=None):
    """Build a full payslip breakdown for one employee and month.

    unpaid_ranges: iterable of (start_date, end_date) for approved unpaid leave.
    """
    unpaid_ranges = unpaid_ranges or []
    period_days = days_in_month(year, month)
    employed = employed_days_in_month(start_date, year, month)
    unpaid = unpaid_leave_days_in_month(
        unpaid_ranges, year, month, employment_start=start_date
    )
    unpaid = min(unpaid, employed)
    eligible = max(employed - unpaid, 0)

    gross = calculate_gross(monthly_salary, eligible, period_days)
    social = calculate_social_security(gross)
    taxable = money(gross - social)
    tax = calculate_income_tax(taxable)
    net = money(gross - social - tax)

    return {
        "year": year,
        "month": month,
        "days_in_month": period_days,
        "employed_days": employed,
        "unpaid_leave_days": unpaid,
        "eligible_days": eligible,
        "monthly_salary": money(monthly_salary),
        "gross_pay": gross,
        "social_security": social,
        "taxable_income": taxable,
        "income_tax": tax,
        "net_pay": net,
    }
