from app.extensions import db


PERIOD_STATUSES = ("draft", "finalized")


class PayrollPeriod(db.Model):
    __tablename__ = "payroll_periods"
    __table_args__ = (
        db.UniqueConstraint("year", "month", name="uq_period_year_month"),
    )

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    # Draft periods can be regenerated; finalized ones are locked.
    status = db.Column(db.String(20), nullable=False, default="draft")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    payslips = db.relationship("Payslip", backref="period", lazy=True)

    def __repr__(self):
        return f"<PayrollPeriod {self.year}-{self.month:02d} {self.status}>"


class Payslip(db.Model):
    __tablename__ = "payslips"
    __table_args__ = (
        db.UniqueConstraint("period_id", "employee_id", name="uq_payslip_period_employee"),
    )

    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(
        db.Integer, db.ForeignKey("payroll_periods.id"), nullable=False
    )
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    gross_pay = db.Column(db.Numeric(10, 2), nullable=False)
    social_security = db.Column(db.Numeric(10, 2), nullable=False)
    income_tax = db.Column(db.Numeric(10, 2), nullable=False)
    net_pay = db.Column(db.Numeric(10, 2), nullable=False)
    # Snapshot of the calculation inputs (eligible days, unpaid days, taxable
    # amount) so a payslip can be explained after salaries or rules change.
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    employee = db.relationship("Employee", backref="payslips")

    def __repr__(self):
        return f"<Payslip period={self.period_id} employee={self.employee_id}>"
