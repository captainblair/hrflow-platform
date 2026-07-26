from flask import Blueprint, jsonify

from app.services import dashboard_service

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("")
def dashboard():
    return jsonify(dashboard_service.get_dashboard())
