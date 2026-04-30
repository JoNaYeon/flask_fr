from datetime import datetime, timezone

from flask import Blueprint, abort, jsonify, render_template, request

from services.item_service import get_all_items, get_item

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/items")
def items_page():
    return render_template("items.html", items=get_all_items())


@main_bp.route("/api/ping")
def ping():
    return jsonify(status="ok", time=datetime.now(timezone.utc).isoformat())


@main_bp.route("/api/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify(received=data)


@main_bp.route("/api/items")
def api_items():
    return jsonify(get_all_items())


@main_bp.route("/api/items/<int:item_id>")
def api_item(item_id: int):
    item = get_item(item_id)
    if item is None:
        abort(404)
    return jsonify(item)
