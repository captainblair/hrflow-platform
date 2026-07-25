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
