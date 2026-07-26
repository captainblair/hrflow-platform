from datetime import date

from app.extensions import db
from app.models import LeaveRequest, PayrollPeriod, Payslip


def test_generate_persists_payslips_for_eligible_active_employees(
    client, employee_factory
):
    first = employee_factory("Alice", salary=10000)
    second = employee_factory("Brian", salary=14000)
    employee_factory("Inactive", is_active=False)
    employee_factory("Future", start_date=date(2026, 8, 1))
    db.session.add(
        LeaveRequest(
            employee_id=second.id,
            leave_type="unpaid",
            start_date=date(2026, 7, 10),
            end_date=date(2026, 7, 12),
            status="approved",
        )
    )
    db.session.commit()

    response = client.post(
        "/api/payroll/generate",
        json={"year": 2026, "month": 7},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["payslip_count"] == 2
    assert PayrollPeriod.query.count() == 1
    assert Payslip.query.count() == 2
    brian = next(p for p in data["payslips"] if p["employee_id"] == second.id)
    assert brian["details"]["unpaid_leave_days"] == 3
    assert brian["gross_pay"] == 12645.16
    assert {p["employee_id"] for p in data["payslips"]} == {first.id, second.id}


def test_regenerating_draft_replaces_instead_of_duplicates(
    client, employee_factory
):
    employee_factory("Alice")

    first = client.post(
        "/api/payroll/generate", json={"year": 2026, "month": 7}
    )
    second = client.post(
        "/api/payroll/generate", json={"year": 2026, "month": 7}
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert PayrollPeriod.query.count() == 1
    assert Payslip.query.count() == 1


def test_finalized_period_cannot_be_regenerated(client, employee_factory):
    employee_factory("Alice")
    generated = client.post(
        "/api/payroll/generate", json={"year": 2026, "month": 7}
    )
    period_id = generated.get_json()["period"]["id"]

    finalized = client.post(f"/api/payroll/periods/{period_id}/finalize")
    regenerated = client.post(
        "/api/payroll/generate", json={"year": 2026, "month": 7}
    )

    assert finalized.status_code == 200
    assert finalized.get_json()["status"] == "finalized"
    assert regenerated.status_code == 400
    assert regenerated.get_json()["error"] == (
        "Payroll period is finalized and cannot be regenerated"
    )
