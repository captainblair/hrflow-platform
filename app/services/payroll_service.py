from decimal import Decimal

from app.extensions import db
from app.models import Employee, LeaveRequest, PayrollPeriod, Payslip
from app.services.payroll_calc import calculate_payslip, month_bounds
from app.utils.errors import ApiError


def _unpaid_ranges_for_employee(employee_id):
    leaves = LeaveRequest.query.filter_by(
        employee_id=employee_id,
        leave_type="unpaid",
        status="approved",
    ).all()
    return [(leave.start_date, leave.end_date) for leave in leaves]


def _breakdown_to_floats(result):
    return {
        key: float(value) if isinstance(value, Decimal) else value
        for key, value in result.items()
    }


def preview_employee_payslip(employee_id, year, month):
    if month < 1 or month > 12:
        raise ApiError("month must be between 1 and 12")

    employee = db.session.get(Employee, employee_id)
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
    payload.update(_breakdown_to_floats(result))
    return payload


def _validate_year_month(year, month):
    if month < 1 or month > 12:
        raise ApiError("month must be between 1 and 12")
    if year < 2000 or year > 2100:
        raise ApiError("year looks invalid")


def generate_payroll(year, month):
    """Create or regenerate a draft payroll period and payslips for active staff."""
    _validate_year_month(year, month)

    period = PayrollPeriod.query.filter_by(year=year, month=month).first()
    if period and period.status == "finalized":
        raise ApiError("Payroll period is finalized and cannot be regenerated")

    if period is None:
        period = PayrollPeriod(year=year, month=month, status="draft")
        db.session.add(period)
        db.session.flush()
    else:
        # Draft re-run: wipe previous slips so numbers stay in sync with
        # current salaries and leave.
        Payslip.query.filter_by(period_id=period.id).delete()

    _, month_end = month_bounds(year, month)
    active = Employee.query.filter_by(is_active=True).order_by(Employee.name).all()
    created = []

    for employee in active:
        if employee.start_date > month_end:
            continue

        breakdown = calculate_payslip(
            monthly_salary=employee.salary,
            start_date=employee.start_date,
            year=year,
            month=month,
            unpaid_ranges=_unpaid_ranges_for_employee(employee.id),
        )

        payslip = Payslip(
            period_id=period.id,
            employee_id=employee.id,
            gross_pay=breakdown["gross_pay"],
            social_security=breakdown["social_security"],
            income_tax=breakdown["income_tax"],
            net_pay=breakdown["net_pay"],
            details=_breakdown_to_floats(breakdown),
        )
        db.session.add(payslip)
        created.append(payslip)

    db.session.commit()
    return period, created


def finalize_period(period_id):
    period = db.session.get(PayrollPeriod, period_id)
    if period is None:
        raise ApiError("Payroll period not found", status_code=404)
    if period.status == "finalized":
        raise ApiError("Payroll period is already finalized")
    period.status = "finalized"
    db.session.commit()
    return period


def list_periods():
    return PayrollPeriod.query.order_by(
        PayrollPeriod.year.desc(), PayrollPeriod.month.desc()
    ).all()


def get_period(period_id):
    period = db.session.get(PayrollPeriod, period_id)
    if period is None:
        raise ApiError("Payroll period not found", status_code=404)
    return period


def list_payslips_for_period(period_id):
    period = get_period(period_id)
    return (
        Payslip.query.filter_by(period_id=period.id)
        .order_by(Payslip.employee_id)
        .all()
    )


def get_payslip(payslip_id):
    payslip = db.session.get(Payslip, payslip_id)
    if payslip is None:
        raise ApiError("Payslip not found", status_code=404)
    return payslip
