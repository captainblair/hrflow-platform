from datetime import date, timedelta

from app.models import LeaveBalance


def test_manager_approval_deducts_annual_balance(client, employee_factory):
    manager = employee_factory("Manager", team="Management")
    employee = employee_factory("Employee", manager_id=manager.id)
    start = date.today() + timedelta(days=10)

    response = client.post(
        "/api/leave",
        json={
            "employee_id": employee.id,
            "leave_type": "annual",
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=2)).isoformat(),
        },
    )
    assert response.status_code == 201
    leave_id = response.get_json()["id"]

    response = client.post(
        f"/api/leave/{leave_id}/approve",
        json={"approver_id": manager.id},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "approved"
    balance = LeaveBalance.query.filter_by(
        employee_id=employee.id, year=start.year
    ).one()
    assert balance.annual_used == 3
    assert balance.annual_remaining == 18


def test_non_manager_cannot_decide_request(client, employee_factory):
    manager = employee_factory("Manager", team="Management")
    other_manager = employee_factory("Other Manager", team="Management")
    employee = employee_factory("Employee", manager_id=manager.id)
    start = date.today() + timedelta(days=10)
    response = client.post(
        "/api/leave",
        json={
            "employee_id": employee.id,
            "leave_type": "sick",
            "start_date": start.isoformat(),
            "end_date": start.isoformat(),
        },
    )
    leave_id = response.get_json()["id"]

    response = client.post(
        f"/api/leave/{leave_id}/reject",
        json={"approver_id": other_manager.id},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Only the employee's manager can decide this request"
    )


def test_insufficient_balance_blocks_approval(client, employee_factory):
    manager = employee_factory("Manager", team="Management")
    employee = employee_factory("Employee", manager_id=manager.id)
    start = date.today() + timedelta(days=10)
    balance = LeaveBalance(
        employee_id=employee.id,
        year=start.year,
        annual_allocated=1,
        annual_used=0,
    )
    from app.extensions import db

    db.session.add(balance)
    db.session.commit()

    response = client.post(
        "/api/leave",
        json={
            "employee_id": employee.id,
            "leave_type": "annual",
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=1)).isoformat(),
        },
    )
    leave_id = response.get_json()["id"]

    response = client.post(
        f"/api/leave/{leave_id}/approve",
        json={"approver_id": manager.id},
    )

    assert response.status_code == 400
    assert "Insufficient annual leave balance" in response.get_json()["error"]
    assert balance.annual_used == 0
