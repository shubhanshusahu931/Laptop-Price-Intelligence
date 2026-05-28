# app.py — LaptopPredict Main Application (v2 with Auth)
import os
from flask import Flask, send_from_directory

try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

from database import init_db
from routes.predict  import predict_bp
from routes.history  import history_bp
from routes.wishlist import wishlist_bp
from routes.compare  import compare_bp
from routes.auth     import auth_bp

BASE     = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.join(BASE, "frontend")

app = Flask(__name__, static_folder=FRONTEND, static_url_path="")

if HAS_CORS:
    CORS(app)
else:
    @app.after_request
    def add_cors(response):
        response.headers['Access-Control-Allow-Origin']  = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        return response

app.register_blueprint(predict_bp)
app.register_blueprint(history_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(compare_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return send_from_directory(FRONTEND, "home.html")

@app.route("/app")
def app_page():
    return send_from_directory(FRONTEND, "search_predict.html")

@app.route("/build")
def build_page():
    return send_from_directory(FRONTEND, "build_estimate.html")

@app.route("/history-page")
def history_page():
    return send_from_directory(FRONTEND, "history.html")

@app.route("/wishlist-page")
def wishlist_page():
    return send_from_directory(FRONTEND, "wishlist.html")

@app.route("/cpu-compare")
def cpu_compare_page():
    return send_from_directory(FRONTEND, "cpu_compare.html")

@app.route("/login")
def login_page():
    return send_from_directory(FRONTEND, "login.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND, filename)

init_db()

if __name__ == "__main__":
    print("\n🚀  LaptopPredict v2 → http://localhost:8000")
    print("   /        → Home Page")
    print("   /app     → Search & Predict")
    print("   /login   → Login / Register\n")
    app.run(debug=True, port=8000)
