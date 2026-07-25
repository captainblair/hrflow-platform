from app.extensions import db


LEAVE_TYPES = ("annual", "sick", "unpaid")
LEAVE_STATUSES = ("pending", "approved", "rejected", "cancelled")


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    leave_type = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    reason = db.Column(db.Text, nullable=True)
    # Set when a manager approves or rejects; used to spot stale requests.
    decided_at = db.Column(db.DateTime, nullable=True)
    decided_by = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    employee = db.relationship(
        "Employee", foreign_keys=[employee_id], backref="leave_requests"
    )
    decider = db.relationship("Employee", foreign_keys=[decided_by])

    def __repr__(self):
        return f"<LeaveRequest {self.id} {self.leave_type} {self.status}>"


class LeaveBalance(db.Model):
    __tablename__ = "leave_balances"
    __table_args__ = (
        db.UniqueConstraint("employee_id", "year", name="uq_balance_employee_year"),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    # Only annual leave draws from a balance. Sick leave is uncapped for now
    # and unpaid leave is handled through payroll instead.
    annual_allocated = db.Column(db.Integer, nullable=False, default=21)
    annual_used = db.Column(db.Integer, nullable=False, default=0)

    employee = db.relationship("Employee", backref="leave_balances")

    @property
    def annual_remaining(self):
        return self.annual_allocated - self.annual_used

    def __repr__(self):
        return f"<LeaveBalance employee={self.employee_id} year={self.year}>"
