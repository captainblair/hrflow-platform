from app.routes.employees import employees_bp
from app.routes.health import health_bp


def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(employees_bp, url_prefix="/api/employees")
