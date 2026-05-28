# routes/wishlist.py
# Wishlist is stored on frontend via localStorage.
# This file is a placeholder for future server-side wishlist sync.
from flask import Blueprint, jsonify, request
wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route("/wishlist/sync", methods=["POST"])
def sync_wishlist():
    """Future: Accept wishlist from frontend and save to DB for cross-device sync."""
    data = request.get_json(force=True)
    items = data.get("items", [])
    # TODO: Save to DB per user_id
    return jsonify({"status": "ok", "count": len(items)})
