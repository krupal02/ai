from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os, json, math

from Backend.Chatbot import ChatBot
from Backend.TTS import TTS
from Backend.UserDB import create_user, get_user, get_user_by_pnr, init_db

app = FastAPI(title="AeroGuide API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = ChatBot()
tts = TTS()

# ── Load static data ──────────────────────────────────
FOOD_DB_PATH = os.path.join("Data", "food_database.json")
SECURITY_DB_PATH = os.path.join("Data", "security_procedures.json")
SHOPPING_DB_PATH = os.path.join("Data", "shopping_database.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

food_data = load_json(FOOD_DB_PATH) if os.path.exists(FOOD_DB_PATH) else {"restaurants": [], "cuisine_categories": {}}
security_data = load_json(SECURITY_DB_PATH) if os.path.exists(SECURITY_DB_PATH) else {}
shopping_data = load_json(SHOPPING_DB_PATH) if os.path.exists(SHOPPING_DB_PATH) else {"shops": []}

# ── Pydantic Models ────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    user_profile: str
    user_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserProfileRequest(BaseModel):
    full_name: str
    pnr: Optional[str] = ""
    age_group: Optional[str] = "18-30"
    travel_frequency: Optional[str] = "first_time"
    loyalty_programs: Optional[list] = []
    special_assistance: Optional[list] = []
    language_preference: Optional[str] = "en"
    dietary_preference: Optional[str] = "both"
    dietary_restrictions: Optional[str] = ""
    flight_number: Optional[str] = ""
    departure_airport: Optional[str] = ""
    travel_date: Optional[str] = ""

class FoodSearchRequest(BaseModel):
    cuisine_types: Optional[List[str]] = []
    dietary_filter: Optional[str] = "both"  # veg, non_veg, vegan, jain, both
    sort_by: Optional[str] = "rating"       # rating, price, wait_time
    price_range: Optional[List[str]] = []   # ["₹", "₹₹", "₹₹₹"]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    user_id: Optional[str] = None

# ── Chat Endpoint (Enhanced) ──────────────────────────
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    # Build enriched user context
    user_context = request.user_profile
    if request.user_id:
        profile = get_user(request.user_id)
        if profile:
            user_context = (
                f"Name: {profile['full_name']}, "
                f"Travel Type: {profile['travel_frequency']}, "
                f"Age Group: {profile['age_group']}, "
                f"Diet: {profile['dietary_preference']}, "
                f"Restrictions: {profile['dietary_restrictions']}, "
                f"Special Needs: {', '.join(profile['special_assistance']) if profile['special_assistance'] else 'None'}"
            )

    print(f"[Chat] query='{request.query}' user_id={request.user_id} coords={request.latitude},{request.longitude}")
    response_text = chatbot.get_response(request.query, user_context, request.latitude, request.longitude)
    tts.speak(response_text)
    return {"response": response_text}

# ── User Profile Endpoints ─────────────────────────────
@app.post("/api/users/profile")
async def create_profile(profile: UserProfileRequest):
    result = create_user(profile.dict())
    return result

@app.get("/api/users/{user_id}")
async def get_profile(user_id: str):
    profile = get_user(user_id)
    if profile:
        return profile
    return {"error": "User not found"}

@app.get("/api/users/pnr/{pnr}")
async def get_profile_by_pnr(pnr: str):
    profile = get_user_by_pnr(pnr)
    if profile:
        return profile
    return {"error": "PNR not found"}

# ── Food Recommendation Endpoints ──────────────────────
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@app.get("/api/food/categories")
async def get_food_categories():
    return {"categories": food_data.get("cuisine_categories", {})}

@app.post("/api/food/recommendations")
async def get_food_recommendations(request: FoodSearchRequest):
    restaurants = food_data.get("restaurants", [])
    results = []

    # Get user dietary preference from profile if available
    user_diet = request.dietary_filter
    if request.user_id:
        profile = get_user(request.user_id)
        if profile and user_diet == "both":
            user_diet = profile.get("dietary_preference", "both")

    for r in restaurants:
        # Cuisine filter
        if request.cuisine_types:
            match = False
            for ct in request.cuisine_types:
                if ct.lower() in [c.lower() for c in r.get("cuisine_types", [])]:
                    match = True
                    break
            if not match:
                continue

        # Dietary filter
        opts = r.get("dietary_options", {})
        if user_diet == "veg" and not opts.get("vegetarian"):
            continue
        if user_diet == "vegan" and not opts.get("vegan"):
            continue
        if user_diet == "jain" and not opts.get("jain"):
            continue

        # Price filter
        if request.price_range and r.get("price_range") not in request.price_range:
            continue

        # Calculate distance
        distance_m = None
        walk_time = None
        if request.latitude and request.longitude:
            coords = r.get("coordinates", {})
            if coords:
                distance_m = haversine_distance(
                    request.latitude, request.longitude,
                    coords.get("lat", 0), coords.get("lon", 0)
                )
                walk_time = max(1, round(distance_m / 80))  # ~80m/min walking

        # Score
        score = 0
        score += (r.get("rating", 3) / 5) * 30
        if distance_m is not None:
            score += max(0, 30 - (distance_m / 20))
        else:
            score += 15
        wait_str = r.get("estimated_wait_time", "10 min")
        try:
            wait_min = int(wait_str.split("-")[0])
        except:
            wait_min = 10
        score += max(0, 20 - wait_min)

        entry = {**r, "distance_m": round(distance_m) if distance_m else None, "walk_time_min": walk_time, "score": round(score, 1)}
        results.append(entry)

    # Sort
    if request.sort_by == "price":
        price_order = {"₹": 1, "₹₹": 2, "₹₹₹": 3}
        results.sort(key=lambda x: price_order.get(x.get("price_range", "₹₹"), 2))
    elif request.sort_by == "wait_time":
        results.sort(key=lambda x: int(x.get("estimated_wait_time", "10").split("-")[0]))
    elif request.sort_by == "distance" and request.latitude:
        results.sort(key=lambda x: x.get("distance_m") or 99999)
    else:
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

    return {"recommendations": results, "total": len(results)}

# ── Security Information Endpoints ─────────────────────
@app.get("/api/security/rules")
async def get_security_rules(airport_code: str = "DEL", flight_type: str = "domestic", destination: str = ""):
    airport = security_data.get("airports", {}).get(airport_code.upper(), {})
    if not airport:
        return {"error": "Airport not found"}

    if flight_type == "international":
        procedures = airport.get("international_security", {})
        # Merge base domestic steps with international additional steps
        all_steps = airport.get("domestic_security", {}).get("steps", []) + procedures.get("additional_steps", [])
        procedures["all_steps"] = all_steps
    else:
        procedures = airport.get("domestic_security", {})
        procedures["all_steps"] = procedures.get("steps", [])

    # Country warnings
    warnings = []
    if destination:
        warnings = security_data.get("country_specific_warnings", {}).get(destination.upper(), [])

    penalties = security_data.get("penalties", {})
    tips = security_data.get("tips", [])

    return {
        "airport_name": airport.get("name", airport_code),
        "procedures": procedures,
        "country_warnings": warnings,
        "penalties": penalties,
        "tips": tips
    }

@app.post("/api/security/check-items")
async def check_items(items: List[str], destination: str = ""):
    airport = security_data.get("airports", {}).get("DEL", {})
    prohibited = airport.get("domestic_security", {}).get("prohibited_items", [])
    restricted = airport.get("domestic_security", {}).get("allowed_with_restrictions", [])

    flagged = []
    for item in items:
        item_lower = item.lower()
        for p in prohibited:
            if item_lower in p.get("item", "").lower() or item_lower in p.get("examples", "").lower():
                flagged.append({"item": item, "status": "prohibited", "detail": p.get("examples", ""), "icon": p.get("icon", "🚫")})
                break
        for r in restricted:
            if item_lower in r.get("item", "").lower():
                flagged.append({"item": item, "status": "restricted", "rule": r.get("rule", ""), "icon": r.get("icon", "⚠️")})
                break

    return {"compliant": len(flagged) == 0, "flagged_items": flagged, "total_checked": len(items)}

# ── Shopping / Duty-Free Endpoints ─────────────────────
@app.get("/api/shopping")
async def get_shops(shop_type: str = ""):
    shops = shopping_data.get("shops", [])
    if shop_type:
        shops = [s for s in shops if s.get("type", "").lower() == shop_type.lower()]
    return {"shops": shops, "total": len(shops)}

@app.get("/api/shopping/offers")
async def get_all_offers():
    all_offers = []
    for shop in shopping_data.get("shops", []):
        for offer in shop.get("offers", []):
            all_offers.append({
                "shop_name": shop.get("name"),
                "shop_type": shop.get("type"),
                "terminal": shop.get("terminal"),
                **offer
            })
    return {"offers": all_offers, "total": len(all_offers)}

# ── Static files ───────────────────────────────────────
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
