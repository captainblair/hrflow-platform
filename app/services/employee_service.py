from datetime import date

from app.extensions import db
from app.models import Employee
from app.models.employee import EMPLOYMENT_TYPES
from app.utils.errors import ApiError


REQUIRED_FIELDS = ("name", "role", "team", "start_date", "salary")


def _parse_start_date(value):
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ApiError("start_date must be an ISO date (YYYY-MM-DD)")


def _validate_manager(manager_id, employee_id=None):
    if manager_id is None:
        return None
    manager = Employee.query.get(manager_id)
    if manager is None:
        raise ApiError("Manager not found", status_code=404)
    if employee_id is not None and manager_id == employee_id:
        raise ApiError("An employee cannot manage themselves")
    return manager


def list_employees(active=None, team=None):
    query = Employee.query
    if active is not None:
        query = query.filter_by(is_active=active)
    if team:
        query = query.filter_by(team=team)
    return query.order_by(Employee.name).all()


def get_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if employee is None:
        raise ApiError("Employee not found", status_code=404)
    return employee


def create_employee(data):
    missing = [f for f in REQUIRED_FIELDS if data.get(f) in (None, "")]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}")

    employment_type = data.get("employment_type", "full_time")
    if employment_type not in EMPLOYMENT_TYPES:
        raise ApiError(
            f"employment_type must be one of: {', '.join(EMPLOYMENT_TYPES)}"
        )

    salary = data["salary"]
    try:
        salary = float(salary)
    except (TypeError, ValueError):
        raise ApiError("salary must be a number")
    if salary < 0:
        raise ApiError("salary cannot be negative")

    _validate_manager(data.get("manager_id"))

    employee = Employee(
        name=data["name"].strip(),
        role=data["role"].strip(),
        team=data["team"].strip(),
        manager_id=data.get("manager_id"),
        start_date=_parse_start_date(data["start_date"]),
        salary=salary,
        employment_type=employment_type,
    )
    db.session.add(employee)
    db.session.commit()
    return employee


def update_employee(employee_id, data):
    employee = get_employee(employee_id)

    if "employment_type" in data:
        if data["employment_type"] not in EMPLOYMENT_TYPES:
            raise ApiError(
                f"employment_type must be one of: {', '.join(EMPLOYMENT_TYPES)}"
            )
        employee.employment_type = data["employment_type"]

    if "manager_id" in data:
        _validate_manager(data["manager_id"], employee_id=employee.id)
        employee.manager_id = data["manager_id"]

    if "salary" in data:
        try:
            salary = float(data["salary"])
        except (TypeError, ValueError):
            raise ApiError("salary must be a number")
        if salary < 0:
            raise ApiError("salary cannot be negative")
        employee.salary = salary

    if "start_date" in data:
        employee.start_date = _parse_start_date(data["start_date"])

    for field in ("name", "role", "team"):
        if field in data:
            value = (data[field] or "").strip()
            if not value:
                raise ApiError(f"{field} cannot be empty")
            setattr(employee, field, value)

    db.session.commit()
    return employee


def deactivate_employee(employee_id):
    employee = get_employee(employee_id)
    if not employee.is_active:
        raise ApiError("Employee is already deactivated")

    # Soft deactivate only. Records are never deleted so payroll history and
    # past leave requests keep pointing at a real employee row.
    employee.is_active = False
    db.session.commit()
    return employee


def build_org_tree():
    employees = Employee.query.order_by(Employee.name).all()
    nodes = {e.id: {"id": e.id, "name": e.name, "role": e.role, "team": e.team, "reports": []} for e in employees}

    roots = []
    for employee in employees:
        node = nodes[employee.id]
        if employee.manager_id and employee.manager_id in nodes:
            nodes[employee.manager_id]["reports"].append(node)
        else:
            roots.append(node)
    return roots
