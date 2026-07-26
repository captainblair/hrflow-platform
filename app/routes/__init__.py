from app.routes.employees import employees_bp
from app.routes.health import health_bp
from app.routes.leave import leave_bp
from app.routes.pages import pages_bp
from app.routes.payroll import payroll_bp


def register_blueprints(app):
    app.register_blueprint(pages_bp)
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(employees_bp, url_prefix="/api/employees")
    app.register_blueprint(leave_bp, url_prefix="/api/leave")
    app.register_blueprint(payroll_bp, url_prefix="/api/payroll")
