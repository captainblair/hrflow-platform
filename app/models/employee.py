from app.extensions import db


EMPLOYMENT_TYPES = ("full_time", "part_time", "contract")


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    team = db.Column(db.String(80), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    employment_type = db.Column(db.String(20), nullable=False, default="full_time")
    # Deactivated employees are kept so leave history and payslips stay valid.
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    manager = db.relationship("Employee", remote_side=[id], backref="reports")

    def __repr__(self):
        return f"<Employee {self.id} {self.name}>"
