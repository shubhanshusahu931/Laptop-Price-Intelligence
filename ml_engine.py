# ml_engine.py — Machine Learning Engine
# Uses: scikit-learn (Random Forest for price prediction, TF-IDF for recommendations)

import re
import math
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import numpy as np

# ─────────────────────────────────────────────
# 1. FEATURE EXTRACTION from laptop title/specs
# ─────────────────────────────────────────────
def extract_features(title: str, specs: str = "") -> dict:
    """
    Title + specs se numeric features nikalta hai ML model ke liye.
    """
    text = (title + " " + specs).lower()

    # RAM (GB)
    ram = 8
    m = re.search(r'(\d+)\s*gb\s*ram|(\d+)gb\s*ddr', text)
    if m:
        ram = int(m.group(1) or m.group(2))

    # Storage (GB)
    storage = 256
    m = re.search(r'(\d+)\s*tb', text)
    if m:
        storage = int(m.group(1)) * 1024
    else:
        m = re.search(r'(\d+)\s*gb\s*(ssd|hdd|storage|nvme)', text)
        if m:
            storage = int(m.group(1))

    # Generation
    gen = 11
    m = re.search(r'(\d+)th\s*gen', text)
    if m:
        gen = int(m.group(1))

    # GPU tier score
    gpu_score = 0
    gpu_tiers = {
        'rtx 4090': 10, 'rtx 4080': 9, 'rtx 4070': 8,
        'rtx 4060': 7, 'rtx 4050': 6,
        'rtx 3080': 8, 'rtx 3070': 7, 'rtx 3060': 6, 'rtx 3050': 5,
        'rx 7900': 9, 'rx 7800': 7, 'rx 7600': 6,
        'arc b580': 6, 'arc a770': 5,
        'm3 max': 9, 'm3 pro': 7, 'm3': 6, 'm2': 5, 'm1': 4,
        'iris xe': 2, 'integrated': 1, 'uhd': 1
    }
    for gpu, score in gpu_tiers.items():
        if gpu in text:
            gpu_score = max(gpu_score, score)
            break

    # CPU tier score
    cpu_score = 5
    cpu_map = {
        'ultra 9': 10, 'ultra 7': 9, 'ultra 5': 8,
        'i9': 9, 'i7': 7, 'i5': 5, 'i3': 3,
        'ryzen 9': 9, 'ryzen ai 9': 10, 'ryzen 7': 7, 'ryzen 5': 5, 'ryzen 3': 3,
        'm4': 10, 'm3': 8, 'm2': 7, 'm1': 6,
        'snapdragon x elite': 8
    }
    for cpu, score in cpu_map.items():
        if cpu in text:
            cpu_score = max(cpu_score, score)
            break

    # Brand premium
    brand_premium = 0
    premiums = {'apple': 3, 'dell': 1, 'hp': 1, 'lenovo': 1,
                'asus': 1, 'msi': 2, 'acer': 0, 'samsung': 2}
    for brand, p in premiums.items():
        if brand in text:
            brand_premium = p
            break

    # Display size
    display = 15.6
    m = re.search(r'(\d+\.?\d*)["\s]*inch|(\d+\.?\d*)"', text)
    if m:
        display = float(m.group(1) or m.group(2))

    # is_gaming
    is_gaming = 1 if any(x in text for x in ['gaming', 'rog', 'tuf', 'legion', 'predator', 'nitro', 'strix']) else 0

    return {
        'ram': ram,
        'storage': storage,
        'generation': gen,
        'gpu_score': gpu_score,
        'cpu_score': cpu_score,
        'brand_premium': brand_premium,
        'display': display,
        'is_gaming': is_gaming
    }


# ─────────────────────────────────────────────
# 2. PRICE PREDICTION MODEL
# ─────────────────────────────────────────────
class PricePredictor:
    """
    Random Forest based price predictor.
    Training data: known laptop specs → prices (manually curated + from DB).
    """

    # Curated training dataset (real Indian market approximate prices)
    TRAINING_DATA = [
        # (ram, storage, gen, gpu_score, cpu_score, brand_premium, display, is_gaming, price)
        (8,  256, 12,  0, 5, 0, 15.6, 0,  42000),
        (8,  512, 12,  0, 5, 1, 15.6, 0,  52000),
        (16, 512, 12,  0, 7, 1, 15.6, 0,  68000),
        (16, 512, 13,  6, 7, 1, 15.6, 1,  85000),
        (16, 512, 13,  7, 7, 2, 15.6, 1, 105000),
        (32, 1024,13,  8, 9, 1, 15.6, 1, 145000),
        (16, 512, 14,  7, 7, 1, 15.6, 0,  90000),
        (16, 512, 14,  8, 9, 1, 16.0, 1, 120000),
        (32, 1024,14,  9, 9, 2, 15.6, 1, 180000),
        (32, 1024,14, 10, 10,2, 17.3, 1, 250000),
        (8,  256, 11,  0, 3, 0, 14.0, 0,  32000),
        (8,  512, 11,  0, 5, 0, 15.6, 0,  45000),
        (16, 512, 12,  5, 5, 0, 15.6, 1,  65000),
        (16, 512, 13,  6, 7, 0, 15.6, 1,  78000),
        (8,  256, 10,  0, 3, 0, 14.0, 0,  28000),
        (16, 512,  8, 10, 9, 3, 13.3, 0,  99000),  # Apple M1
        (16, 512,  8,  9, 9, 3, 13.3, 0, 125000),  # Apple M2
        (18,1024,  8, 10,10, 3, 14.2, 0, 165000),  # Apple M3 Pro
        (16, 512, 13,  5, 5, 0, 15.6, 0,  55000),
        (32, 512, 14,  0, 8, 1, 13.3, 0,  85000),
        (16, 512, 12,  6, 7, 1, 15.6, 1,  75000),
        (16,1024, 13,  7, 7, 2, 16.0, 1,  98000),
        (32,1024, 14,  8, 9, 1, 15.6, 1, 135000),
        (64,2048, 14, 10,10, 2, 17.3, 1, 320000),

        # --- Nayi Rows (Intel i3/i5/i7/i9 Budget & Mid) ---
        (8, 512, 12, 0, 4, 0, 15.6, 0, 38000),
        (16, 512, 12, 0, 6, 0, 14.0, 0, 48000),
        (16, 512, 13, 0, 7, 1, 15.6, 0, 58000),
        (8, 256, 12, 0, 4, 1, 14.0, 0, 41000),
        (16, 1024, 13, 4, 7, 1, 15.6, 0, 72000),
        (16, 512, 14, 5, 8, 2, 14.0, 0, 95000),
        (8, 512, 13, 0, 6, 0, 15.6, 0, 46000),
        (16, 256, 11, 0, 5, 0, 15.6, 0, 39000),
        (32, 1024, 13, 6, 8, 1, 16.0, 0, 88000),
        (16, 1024, 14, 0, 8, 2, 13.4, 0, 115000),

        # --- Intel Core Ultra (AI PCs) ---
        (16, 512, 15, 7, 8, 2, 14.0, 0, 110000),  # Ultra 5
        (16, 1024, 15, 8, 9, 2, 14.0, 0, 125000), # Ultra 7
        (32, 1024, 15, 9, 9, 3, 16.0, 0, 160000), # Ultra 9
        (32, 2048, 15, 9, 10, 3, 14.0, 0, 195000),
        (16, 512, 15, 7, 8, 1, 15.6, 0, 98000),

        # --- AMD Ryzen Series (Budget to High End) ---
        (8, 256, 5, 0, 4, 0, 15.6, 0, 30000),   # R3 5000
        (8, 512, 5, 3, 5, 0, 15.6, 0, 42000),   # R5 5000
        (16, 512, 5, 4, 6, 0, 15.6, 0, 51000),  # R7 5000
        (16, 512, 6, 5, 7, 1, 15.6, 1, 62000),  # R5 6000
        (16, 512, 7, 6, 8, 1, 15.6, 1, 76000),  # R7 7000
        (16, 512, 7, 7, 9, 1, 15.6, 1, 89000),  # R9 7000
        (16, 1024, 8, 8, 9, 2, 16.0, 1, 115000), # R7 8000
        (32, 1024, 8, 9, 9, 2, 15.6, 1, 140000), # R9 8000
        (16, 512, 7, 0, 6, 0, 14.0, 0, 44000),
        (8, 512, 7, 0, 5, 0, 15.6, 0, 37000),
        (32, 1024, 9, 10, 10, 2, 17.3, 1, 230000), # R9 9000 Gaming

        # --- Gaming Laptops (RTX 3050 to 4090) ---
        (16, 512, 12, 5, 6, 0, 15.6, 1, 60000),
        (16, 512, 13, 6, 7, 0, 15.6, 1, 72000),
        (16, 1024, 13, 7, 8, 1, 15.6, 1, 88000),
        (16, 512, 14, 8, 8, 1, 16.0, 1, 110000),
        (32, 1024, 14, 9, 9, 1, 15.6, 1, 155000),
        (32, 1024, 14, 10, 10, 2, 16.0, 1, 210000),
        (16, 512, 12, 6, 7, 1, 15.6, 1, 79000),
        (16, 512, 13, 7, 8, 2, 15.6, 1, 105000), # ROG/Alienware
        (32, 2048, 14, 10, 10, 3, 18.0, 1, 380000), # Ultra High End
        (16, 1024, 12, 5, 7, 0, 15.6, 1, 68000),

        # --- Apple MacBooks (M1, M2, M3, M4) ---
        (8, 256, 8, 7, 8, 3, 13.3, 0, 70000),   # M1 Base
        (8, 512, 8, 8, 9, 3, 13.6, 0, 95000),   # M2 Base
        (16, 256, 8, 9, 9, 3, 15.3, 0, 115000), # M2 15-inch
        (16, 512, 8, 10, 10, 3, 14.2, 0, 185000), # M3 Pro
        (32, 1024, 8, 10, 10, 3, 16.2, 0, 245000), # M3 Max
        (16, 512, 8, 10, 10, 3, 14.0, 0, 155000), # M4 (Coming/Est)
        (24, 512, 8, 9, 9, 3, 13.6, 0, 145000),
        (8, 256, 8, 7, 8, 3, 13.3, 0, 65000),   # Refurb/Old Stock M1

        # --- Professional/Thin & Light ---
        (16, 512, 13, 0, 7, 2, 13.4, 0, 105000), # XPS 13
        (32, 1024, 14, 0, 9, 2, 14.0, 0, 145000), # Zenbook OLED
        (16, 512, 14, 0, 8, 1, 13.3, 0, 82000),
        (16, 1024, 13, 0, 7, 1, 14.0, 0, 75000),
        (8, 512, 12, 0, 5, 2, 13.3, 0, 68000),   # Surface
        (16, 256, 13, 0, 6, 1, 15.6, 0, 59000),

        # --- Miscellaneous & New Entries to fill 100 ---
        (8, 256, 11, 0, 3, 0, 15.6, 0, 31000),
        (16, 512, 14, 4, 8, 0, 15.6, 0, 64000),
        (32, 1024, 13, 7, 8, 1, 16.0, 1, 118000),
        (16, 512, 12, 4, 6, 0, 15.6, 1, 56000),
        (8, 512, 13, 0, 5, 0, 14.0, 0, 43000),
        (16, 1024, 14, 6, 8, 1, 15.6, 1, 92000),
        (16, 512, 12, 0, 7, 2, 13.5, 0, 112000),
        (32, 2048, 14, 10, 10, 2, 17.3, 1, 285000),
        (16, 512, 13, 5, 7, 1, 15.6, 1, 81000),
        (8, 256, 10, 0, 2, 0, 15.6, 0, 25000),
        (16, 512, 14, 0, 8, 1, 14.0, 0, 77000),
        (32, 1024, 15, 8, 9, 2, 16.0, 0, 148000),
        (16, 1024, 6, 5, 7, 0, 15.6, 1, 59000),
        (16, 512, 13, 0, 7, 0, 15.6, 0, 53000),
        (8, 512, 12, 0, 4, 0, 15.6, 0, 39500),
        (32, 512, 14, 7, 9, 1, 15.6, 1, 128000),
        (16, 512, 13, 6, 7, 1, 14.0, 1, 84000),
        (16, 1024, 14, 0, 9, 2, 15.6, 0, 135000),
        (8, 256, 11, 0, 4, 1, 14.0, 0, 44000),
        (16, 512, 12, 5, 6, 0, 15.6, 1, 61000),
        (32, 1024, 14, 9, 10, 2, 16.0, 1, 195000),
        (16, 512, 15, 7, 8, 1, 14.0, 0, 102000),
        (16, 512, 13, 4, 7, 0, 15.6, 0, 57000),
        (8, 512, 12, 0, 5, 0, 15.6, 0, 42500),
        (16, 1024, 14, 8, 9, 1, 15.6, 1, 132000),
        (32, 1024, 14, 10, 10, 3, 14.0, 0, 215000),
        (16, 512, 13, 0, 7, 1, 15.6, 0, 66000),
        (8, 256, 12, 0, 4, 0, 14.0, 0, 36000),
        (16, 512, 5, 4, 6, 0, 15.6, 0, 49000),
        (16, 1024, 14, 0, 8, 1, 16.0, 0, 89000)
]

    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_split=2,
            random_state=42
        )
        self._train()

    def _train(self):
        X = [[d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7]] for d in self.TRAINING_DATA]
        y = [d[8] for d in self.TRAINING_DATA]
        self.model.fit(X, y)

    def add_real_data(self, products: list):
        """DB se real data add karke model retrain karo"""
        if len(products) < 3:
            return
        extra_X, extra_y = [], []
        for p in products:
            if p.get('price_value', 0) > 10000:
                feats = extract_features(p.get('title',''), p.get('specs',''))
                extra_X.append([
                    feats['ram'], feats['storage'], feats['generation'],
                    feats['gpu_score'], feats['cpu_score'],
                    feats['brand_premium'], feats['display'], feats['is_gaming']
                ])
                extra_y.append(p['price_value'])
        if extra_X:
            base_X = [[d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7]] for d in self.TRAINING_DATA]
            base_y = [d[8] for d in self.TRAINING_DATA]
            self.model.fit(base_X + extra_X, base_y + extra_y)

    def predict(self, title: str, specs: str = "") -> dict:
        """
        Ek laptop ka predicted price + confidence range return karta hai.
        """
        feats = extract_features(title, specs)
        X = [[feats['ram'], feats['storage'], feats['generation'],
              feats['gpu_score'], feats['cpu_score'],
              feats['brand_premium'], feats['display'], feats['is_gaming']]]

        pred = self.model.predict(X)[0]

        # Confidence range: ±12%
        low  = int(pred * 0.88)
        high = int(pred * 1.12)

        return {
            'predicted_price': int(pred),
            'range_low':  low,
            'range_high': high,
            'features':   feats
        }

    def is_good_deal(self, actual_price: int, predicted_price: int) -> dict:
        """
        Actual vs predicted compare karke deal quality batao.
        """
        if predicted_price == 0:
            return {'label': 'Unknown', 'color': 'grey', 'diff_pct': 0}

        diff_pct = ((actual_price - predicted_price) / predicted_price) * 100

        if diff_pct <= -15:
            return {'label': '🔥 Hot Deal', 'color': 'green', 'diff_pct': round(diff_pct, 1)}
        elif diff_pct <= -5:
            return {'label': '✅ Good Price', 'color': 'lightgreen', 'diff_pct': round(diff_pct, 1)}
        elif diff_pct <= 5:
            return {'label': '➡️ Fair Price', 'color': 'orange', 'diff_pct': round(diff_pct, 1)}
        else:
            return {'label': '⚠️ Overpriced', 'color': 'red', 'diff_pct': round(diff_pct, 1)}


# ─────────────────────────────────────────────
# 3. ML-BASED RECOMMENDER (TF-IDF + Cosine)
# ─────────────────────────────────────────────
class MLRecommender:
    """
    TF-IDF vectorizer se laptop text similarity score nikalta hai.
    User ki query se match karta hai — rule-based se zyada smart.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            max_features=500,
            stop_words='english'
        )

    def recommend(self, products: list, user_filters: dict, budget: int = 0, top_n: int = 5) -> list:
        if not products:
            return []

        # User query string banana
        parts = []
        for key in ['brand', 'processor', 'generation', 'ram', 'gpu']:
            v = user_filters.get(key, '')
            if v and v.lower() not in ['any', '']:
                parts.append(v)
        storage = user_filters.get('storage', '')
        if storage and storage not in ['any', '']:
            parts.append(f"{storage}GB SSD")

        user_query = " ".join(parts) if parts else "laptop"

        # Corpus banana (title + specs)
        corpus = [f"{p.get('title','')} {p.get('specs','')}" for p in products]
        corpus_with_query = corpus + [user_query]

        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus_with_query)
        except Exception:
            return products[:top_n]

        # Query vector (last row) vs all products
        query_vec = tfidf_matrix[-1]
        product_vecs = tfidf_matrix[:-1]
        similarities = cosine_similarity(query_vec, product_vecs)[0]

        # Score combine: TF-IDF similarity + budget bonus
        scored = []
        for i, p in enumerate(products):
            price = p.get('price_value', 0)

            # Budget hard filter
            if budget > 0 and price > (budget + 5000):
                continue

            tfidf_score = float(similarities[i])

            # Budget bonus
            budget_bonus = 0.0
            if budget > 0 and 0 < price <= budget:
                budget_bonus = 0.15 * (1 - price / budget)

            # Deal bonus
            deal_bonus = 0.0
            deal = p.get('deal')
            if deal:
                lbl = deal.get('label', '')
                if 'Hot'  in lbl: deal_bonus += 0.20
                elif 'Good' in lbl: deal_bonus += 0.10
                elif 'Over' in lbl: deal_bonus -= 0.05

            # Below ML price bonus
            pv   = p.get('price_value', 0)
            pred = p.get('predicted_price')
            if pred and pv and pv < pred: deal_bonus += 0.12

            # Rating bonus
            try:
                rat = float(p.get('rating') or 0)
                if rat >= 4.5: deal_bonus += 0.08
                elif rat >= 4.0: deal_bonus += 0.04
            except: pass

            final_score = tfidf_score + budget_bonus + deal_bonus

            # Lower threshold — always include deals even if TF-IDF is low
            threshold = 0.001 if (deal_bonus > 0) else 0.01
            if final_score > threshold:
                p = dict(p)
                p['ml_score'] = round(min(final_score * 100, 99), 1)
                scored.append((final_score, p))

        scored.sort(key=lambda x: -x[0])
        result = [item[1] for item in scored[:top_n]]

        # Fallback: if TF-IDF gave nothing, use deal-based ranking
        if not result and products:
            fallback = []
            for p in products:
                price = p.get('price_value', 0)
                if budget > 0 and price > (budget + 5000): continue
                fb_score = 0
                deal = p.get('deal')
                if deal:
                    lbl = deal.get('label', '')
                    if 'Hot'  in lbl: fb_score += 50
                    elif 'Good' in lbl: fb_score += 30
                pv   = p.get('price_value', 0)
                pred = p.get('predicted_price')
                if pred and pv and pv < pred: fb_score += 25
                try:
                    rat = float(p.get('rating') or 0)
                    if rat >= 4.5: fb_score += 20
                except: pass
                if fb_score > 0:
                    p = dict(p)
                    p['ml_score'] = round(fb_score, 1)
                    fallback.append((fb_score, p))
            fallback.sort(key=lambda x: -x[0])
            result = [item[1] for item in fallback[:top_n]]

        return result


# Singleton instances
_price_predictor = None
_ml_recommender  = None

def get_price_predictor():
    global _price_predictor
    if _price_predictor is None:
        _price_predictor = PricePredictor()
    return _price_predictor

def get_ml_recommender():
    global _ml_recommender
    if _ml_recommender is None:
        _ml_recommender = MLRecommender()
    return _ml_recommender
