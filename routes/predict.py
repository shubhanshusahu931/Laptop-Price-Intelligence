# routes/predict.py
from flask import Blueprint, request, jsonify
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_db_connection
from serpapi_client import fetch_laptop_prices

try:
    from ml_engine import get_price_predictor, get_ml_recommender, estimate_demand
    ML_ON = True
except ImportError:
    ML_ON = False

try:
    from recommender import recommend_products
    REC_ON = True
except ImportError:
    REC_ON = False

predict_bp = Blueprint('predict', __name__)

ALLOWED = ["amazon","flipkart","croma","cashify","reliance digital","swappa","ebay","gadgetnow"]

@predict_bp.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)

    brand      = data.get("brand","")
    processor  = data.get("processor","")
    generation = data.get("generation","")
    ram        = data.get("ram","")
    storage    = data.get("storage","")
    gpu        = data.get("gpu","")
    display    = data.get("display","15.6")
    budget     = int(data.get("budget",0) or 0)

    # Build query
    parts = [x for x in [brand,processor,generation,gpu] if x and x!="Any"]
    search_query = (" ".join(parts) + " laptop") if parts else "latest laptops india"
    print(f"Search: {search_query}")

    # Fetch
    try: api_results = fetch_laptop_prices(search_query)
    except Exception as e: print(f"API error: {e}"); api_results = []

    predictor = get_price_predictor() if ML_ON else None
    conn = get_db_connection()

    # Retrain with DB data
    if predictor:
        try:
            rows = conn.execute("SELECT title,price,specs_summary FROM laptop_results WHERE price>10000 LIMIT 50").fetchall()
            predictor.add_real_data([{"title":r["title"],"price_value":r["price"],"specs":r["specs_summary"]} for r in rows])
        except: pass

    laptops = []
    fallback_specs = f"{brand} {processor} {generation} {ram} {storage}GB {gpu} {display}\""

    for item in api_results:
        site = item.get("platform","").lower()
        if not any(a in site for a in ALLOWED): continue

        pv    = item.get("price_value",0)
        title = item.get("title","Laptop")
        specs = item.get("specs") or fallback_specs

        entry = {
            "title":   title, "price": item.get("price_str","N/A"), "price_value": pv,
            "platform":item.get("platform","Online"), "image": item.get("image",""),
            "link":    item.get("link","#"),           "rating":item.get("rating",""),
            "ram":     item.get("ram",""),             "ram_type":item.get("ram_type",""),
            "storage": item.get("storage",""),         "storage_type":item.get("storage_type",""),
            "specs":   specs, "predicted_price": None, "deal": None
        }

        # ML price prediction
        if predictor and pv>0:
            try:
                pr = predictor.predict(title, specs)
                entry["predicted_price"] = pr["predicted_price"]
                entry["deal"] = predictor.is_good_deal(pv, pr["predicted_price"])
            except: pass

        # Budget filter
        if budget>0 and pv>(budget+5000): continue
        laptops.append(entry)

        # Save to DB
        try:
            conn.execute("""
                INSERT OR REPLACE INTO laptop_results
                (title,price,link,platform,image,ram,ram_type,storage,storage_type,rating,specs_summary,predicted_price,timestamp)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
            """, (title,pv,entry["link"],entry["platform"],entry["image"],entry["ram"],entry["ram_type"],
                  entry["storage"],entry["storage_type"],entry["rating"],specs,entry.get("predicted_price")))
        except Exception as e: print(f"DB err: {e}")

    conn.commit()
    conn.close()

    # Recommendations
    recommended = []
    try:
        if ML_ON:   recommended = get_ml_recommender().recommend(laptops, data, budget=budget)
        elif REC_ON: recommended = recommend_products(laptops, data)
    except Exception as e:
        print(f"Recommender error: {e}")

    # Attach rec_tags + rec_reason for frontend rendering
    for r in recommended:
        tags, reasons = [], []
        pv   = r.get('price_value', 0)
        pred = r.get('predicted_price')
        deal = r.get('deal')
        rat  = r.get('rating', '')
        ram  = r.get('ram', 0)
        score= r.get('ml_score', 0)
        try: rat_f = float(rat) if rat else 0.0
        except: rat_f = 0.0
        try: ram_i = int(ram) if ram else 0
        except: ram_i = 0

        if deal:
            lbl = deal.get('label', '')
            if 'Hot'  in lbl: tags.append('🔥 Hot Deal')
            if 'Good' in lbl: tags.append('✅ Good Price')
        if pred and pv and pv < pred:
            tags.append('💰 Below ML Price')
            reasons.append(f"₹{(pred-pv):,} below fair value")
        if rat_f >= 4.5: tags.append('⭐ Top Rated')
        if ram_i >= 32:  tags.append('🧠 High RAM')
        if score > 70:   tags.append('🎯 Best Match')
        if budget > 0 and 0 < pv <= budget: tags.append('✅ In Budget')
        r['rec_tags']   = tags[:4]   # max 4 tags
        r['rec_reason'] = reasons[0] if reasons else ''

    # ML summary
    ml_summary = None
    if ML_ON and laptops:
        try:
            hot   = sum(1 for l in laptops if l.get("deal") and "Hot"       in l["deal"].get("label",""))
            over  = sum(1 for l in laptops if l.get("deal") and "Overpriced" in l["deal"].get("label",""))
            avg_p = int(sum(l["price_value"] for l in laptops if l["price_value"]) / max(len(laptops),1))
            parts2 = [f"Found {len(laptops)} laptops (avg \u20B9{avg_p:,})."]
            if hot:  parts2.append(f"\uD83D\uDD25 {hot} hot deals below market price.")
            if over: parts2.append(f"\u26A0\uFE0F {over} overpriced listings detected.")
            ml_summary = " ".join(parts2)
        except: pass

    return jsonify({"total_results":len(laptops),"results":laptops,"recommended":recommended,"ml_summary":ml_summary})
