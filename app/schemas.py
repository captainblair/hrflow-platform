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
        "year": balance.year,
        "annual_allocated": balance.annual_allocated,
        "annual_used": balance.annual_used,
        "annual_remaining": balance.annual_remaining,
    }
