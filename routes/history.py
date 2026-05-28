# routes/history.py
from flask import Blueprint, jsonify
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_db_connection

history_bp = Blueprint('history', __name__)

@history_bp.route("/history", methods=["GET"])
def get_history():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM laptop_results ORDER BY timestamp DESC LIMIT 8").fetchall()
    conn.close()
    return jsonify([{
        "title":   r["title"], "price": f"\u20B9{r['price']:,}" if r["price"] else "N/A",
        "price_value": r["price"], "image": r["image"], "link": r["link"],
        "platform":r["platform"], "ram": r["ram"], "storage": r["storage"],
        "rating":  r["rating"], "specs": r["specs_summary"],
        "predicted_price": r["predicted_price"]
    } for r in rows])

@history_bp.route("/history/clear", methods=["DELETE"])
def clear_history():
    conn = get_db_connection()
    conn.execute("DELETE FROM laptop_results")
    conn.commit(); conn.close()
    return jsonify({"status": "cleared"})
