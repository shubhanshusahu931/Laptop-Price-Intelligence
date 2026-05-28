# recommender.py

def normalize(text):
    """
    Text ko clean karta hai (lowercase, no spaces, no dashes) 
    taaki matching accurate ho.
    """
    if not text: 
        return ""
    return str(text).lower().replace(" ", "").replace("-", "")

def recommend_products(products, user_filters, top_n=5):
    recommendations = []
    
    # 1. User inputs ko normalize karein (Agar empty hai toh skip honge)
    req_brand = normalize(user_filters.get("brand", ""))
    req_cpu = normalize(user_filters.get("processor", ""))
    req_gen = normalize(user_filters.get("generation", "")).replace("gen", "")
    req_ram = normalize(user_filters.get("ram", ""))
    req_storage = normalize(user_filters.get("storage", "")).replace("gb", "")
    req_gpu = normalize(user_filters.get("gpu", ""))
    budget = int(user_filters.get("budget", 0) or 0)

    for p in products:
        price = p.get("price_value", 0)
        
        # 2. Hard Filter: Budget
        # Agar budget set hai aur laptop mehnga hai, toh skip karein
        if budget > 0 and price > (budget + 5000): # 5k ka grace period for better options
            continue

        # Search space: Title + Specs (Database se jo detailed specs hain)
        title = normalize(p.get("title", ""))
        specs = normalize(p.get("specs", ""))
        full_text = title + specs
        
        score = 0

        # 3. Scoring Logic (Sirf un cheezon ka score badhega jo user ne maangi hain)
        
        # Brand Match
        if req_brand and req_brand in full_text:
            score += 6 # Brand match is very important for preference
        
        # CPU Match
        if req_cpu and req_cpu in full_text:
            score += 8  
        
        # GPU Match (Aapka main requirement)
        if req_gpu and req_gpu in full_text:
            score += 15 # Sabse zyada weightage GPU ko diya hai
        
        # Generation Match
        if req_gen and req_gen in full_text:
            score += 8
            
        # RAM Match
        if req_ram and req_ram in full_text:
            score += 4

        # Storage Match
        if req_storage and req_storage in full_text:
            score += 2

        # 4. Result add karein agar score 0 se bada ho
        # (Isse irrelevant results recommendations mein nahi aayenge)
        if score > 0:
            p["score"] = score
            recommendations.append(p)

    # 5. Sort: Pehle high score, fir low price (Value for money)
    recommendations.sort(key=lambda x: (-x["score"], x["price_value"]))

    return recommendations[:top_n]