def serialize_employee(employee):
    return {
        "id": employee.id,
        "name": employee.name,
        "role": employee.role,
        "team": employee.team,
        "manager_id": employee.manager_id,
        "manager_name": employee.manager.name if employee.manager else None,
        "start_date": employee.start_date.isoformat(),
        "salary": float(employee.salary),
        "employment_type": employee.employment_type,
        "is_active": employee.is_active,
    }


def serialize_leave_request(leave):
    from app.services.leave_rules import is_overdue

    return {
        "id": leave.id,
        "employee_id": leave.employee_id,
        "employee_name": leave.employee.name if leave.employee else None,
        "leave_type": leave.leave_type,
        "start_date": leave.start_date.isoformat(),
        "end_date": leave.end_date.isoformat(),
        "days": (leave.end_date - leave.start_date).days + 1,
        "status": leave.status,
        "reason": leave.reason,
        "is_overdue": is_overdue(leave),
        "decided_at": leave.decided_at.isoformat() if leave.decided_at else None,
        "decided_by": leave.decided_by,
        "decided_by_name": leave.decider.name if leave.decider else None,
        "created_at": leave.created_at.isoformat() if leave.created_at else None,
    }


def serialize_leave_balance(balance):
    return {
        "employee_id": balance.employee_id,
        "employee_name": balance.employee.name if balance.employee else None,
        "year": balance.year,
        "annual_allocated": balance.annual_allocated,
        "annual_used": balance.annual_used,
        "annual_remaining": balance.annual_remaining,
    }


def serialize_payroll_period(period):
    return {
        "id": period.id,
        "year": period.year,
        "month": period.month,
        "status": period.status,
        "payslip_count": len(period.payslips) if period.payslips is not None else 0,
        "created_at": period.created_at.isoformat() if period.created_at else None,
    }


def serialize_payslip(payslip):
    return {
        "id": payslip.id,
        "period_id": payslip.period_id,
        "employee_id": payslip.employee_id,
        "employee_name": payslip.employee.name if payslip.employee else None,
        "gross_pay": float(payslip.gross_pay),
        "social_security": float(payslip.social_security),
        "income_tax": float(payslip.income_tax),
        "net_pay": float(payslip.net_pay),
        "details": payslip.details,
        "created_at": payslip.created_at.isoformat() if payslip.created_at else None,
    }
