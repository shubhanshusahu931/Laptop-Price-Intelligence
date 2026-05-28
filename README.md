# Laptop-Price-Intelligence


AI-powered laptop price intelligence platform with login, ML predictions, and real-time price comparison.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your SerpAPI key (already in .env)
# Edit .env and add your key

# 3. Run the app
python app.py
```

Open → **http://localhost:8000**

##  Features

| Feature | Description |
|---------|-------------|
|  Home Page | Landing page with 3D particle animations |
|  Login/Register | Full auth with session management |
|  Switch Account | Manage multiple accounts locally |
|  Search & Predict | Real-time prices + ML price prediction |
|  Build & Estimate | Configure specs and estimate price |
|  History | Past searches stored in SQLite |
|  Wishlist | Save laptops you're watching |
|  CPU Compare | Side-by-side CPU benchmark comparison |

## Project Structure

```
LP2/
├── app.py              # Main Flask app (routes registration)
├── database.py         # SQLite DB + User Auth helpers
├── ml_engine.py        # ML price prediction
├── recommender.py      # Product recommendations
├── serpapi_client.py   # Live price fetching
├── routes/
│   ├── auth.py         # Login, Register, Logout, /me
│   ├── predict.py      # Search & predict endpoint
│   ├── history.py      # Search history
│   ├── wishlist.py     # Wishlist sync
│   └── compare.py      # CPU comparison data
└── frontend/
    ├── home.html           # Landing page (NEW)
    ├── login.html          # Dedicated login/register (NEW)
    ├── search_predict.html # Main app
    ├── build_estimate.html # Build configurator
    ├── history.html        # History page
    ├── wishlist.html       # Wishlist page
    ├── cpu_compare.html    # CPU comparison
    ├── style.css           # Shared styles
    └── _shared.js          # Shared JS (auth, theme, nav)
```

## Auth Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login (username or email) |
| POST | `/auth/logout` | Logout (invalidates session) |
| GET | `/auth/me` | Get current user info |

## Coming Soon

- [ ] Mobile & accessories section
- [ ] Gaming laptops section
- [ ] Price drop alerts
- [ ] User profile page
- [ ] Compare saved laptops

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **ML**: scikit-learn
- **Prices**: SerpAPI
- **Frontend**: Vanilla HTML/CSS/JS
