from app.routes.employees import employees_bp
from app.routes.health import health_bp
from app.routes.leave import leave_bp


def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(employees_bp, url_prefix="/api/employees")
    app.register_blueprint(leave_bp, url_prefix="/api/leave")
