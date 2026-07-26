from datetime import date, datetime, timedelta

import click

from app.extensions import db
from app.models import Employee, LeaveBalance, LeaveRequest


@click.command("seed")
def seed_command():
    """Load a small set of demo employees, balances and leave requests."""
    if Employee.query.first():
        click.echo("Database already has data, skipping seed.")
        return

    grace = Employee(
        name="Grace Wanjiru",
        role="General Manager",
        team="Management",
        start_date=date(2023, 2, 1),
        salary=95000,
        employment_type="full_time",
    )
    db.session.add(grace)
    db.session.flush()

    brian = Employee(
        name="Brian Otieno",
        role="Engineering Lead",
        team="Engineering",
        manager_id=grace.id,
        start_date=date(2023, 9, 18),
        salary=75000,
        employment_type="full_time",
    )
    alice = Employee(
        name="Alice Achieng",
        role="HR Officer",
        team="Operations",
        manager_id=grace.id,
        start_date=date(2024, 5, 6),
        salary=48000,
        employment_type="full_time",
    )
    db.session.add_all([brian, alice])
    db.session.flush()

    faith = Employee(
        name="Faith Njeri",
        role="Backend Engineer",
        team="Engineering",
        manager_id=brian.id,
        start_date=date(2024, 11, 4),
        salary=55000,
        employment_type="full_time",
    )
    kevin = Employee(
        name="Kevin Mutua",
        role="Frontend Engineer",
        team="Engineering",
        manager_id=brian.id,
        start_date=date(2025, 3, 10),
        salary=52000,
        employment_type="full_time",
    )
    daniel = Employee(
        name="Daniel Kiprop",
        role="Accountant",
        team="Operations",
        manager_id=grace.id,
        # Mid-month starter, useful for checking payroll proration.
        start_date=date.today().replace(day=15),
        salary=38000,
        employment_type="part_time",
    )
    wycliffe = Employee(
        name="Wycliffe Barasa",
        role="Support Assistant",
        team="Operations",
        manager_id=alice.id,
        start_date=date(2024, 8, 12),
        salary=30000,
        employment_type="contract",
    )
    db.session.add_all([faith, kevin, daniel, wycliffe])
    db.session.flush()

    everyone = [grace, brian, alice, faith, kevin, daniel, wycliffe]
    year = date.today().year
    for person in everyone:
        db.session.add(
            LeaveBalance(employee_id=person.id, year=year, annual_allocated=21)
        )

    today = date.today()

    db.session.add_all(
        [
            # Fresh request with enough notice, waiting on Brian.
            LeaveRequest(
                employee_id=faith.id,
                leave_type="annual",
                start_date=today + timedelta(days=10),
                end_date=today + timedelta(days=14),
                reason="Family visit upcountry",
            ),
            # Sat unanswered long enough to trip the overdue rule (> 5 business days).
            LeaveRequest(
                employee_id=kevin.id,
                leave_type="annual",
                start_date=today + timedelta(days=20),
                end_date=today + timedelta(days=22),
                reason="Long weekend away",
                created_at=datetime.now() - timedelta(days=14),
            ),
            # Already approved sick leave from earlier in the month.
            LeaveRequest(
                employee_id=alice.id,
                leave_type="sick",
                start_date=today - timedelta(days=6),
                end_date=today - timedelta(days=5),
                status="approved",
                reason="Flu",
                decided_at=datetime.now() - timedelta(days=6),
                decided_by=grace.id,
            ),
            # Approved unpaid leave this month so payroll has something to deduct.
            LeaveRequest(
                employee_id=kevin.id,
                leave_type="unpaid",
                start_date=today - timedelta(days=3),
                end_date=today - timedelta(days=1),
                status="approved",
                reason="Personal matters",
                decided_at=datetime.now() - timedelta(days=4),
                decided_by=brian.id,
            ),
        ]
    )

    db.session.commit()
    click.echo(f"Seeded {len(everyone)} employees with balances and leave requests.")
