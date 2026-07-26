from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Employee


@pytest.fixture
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def employee_factory(app):
    def create_employee(
        name,
        team="Engineering",
        manager_id=None,
        salary=10000,
        start_date=date(2024, 1, 1),
        is_active=True,
    ):
        employee = Employee(
            name=name,
            role="Developer",
            team=team,
            manager_id=manager_id,
            salary=salary,
            start_date=start_date,
            employment_type="full_time",
            is_active=is_active,
        )
        db.session.add(employee)
        db.session.commit()
        return employee

    return create_employee
