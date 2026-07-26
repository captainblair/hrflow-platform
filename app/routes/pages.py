from pathlib import Path

from flask import Blueprint, send_from_directory


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def dashboard_page():
    return send_from_directory(FRONTEND_DIR, "index.html")


@pages_bp.get("/employees")
def employees_page():
    return send_from_directory(FRONTEND_DIR, "employees.html")


@pages_bp.get("/leave")
def leave_page():
    return send_from_directory(FRONTEND_DIR, "leave.html")


@pages_bp.get("/payroll")
def payroll_page():
    return send_from_directory(FRONTEND_DIR, "payroll.html")


@pages_bp.get("/css/<path:filename>")
def css_files(filename):
    return send_from_directory(FRONTEND_DIR / "css", filename)


@pages_bp.get("/js/<path:filename>")
def js_files(filename):
    return send_from_directory(FRONTEND_DIR / "js", filename)
