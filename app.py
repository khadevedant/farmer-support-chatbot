from flask import Flask, render_template, request, jsonify
import json
import re
import random
import requests


app = Flask(__name__)

# ------------------- LOAD DATASETS -------------------
with open("datasets/farmer_dataset.json", "r", encoding="utf-8") as f:
    FARMER_DATASET = json.load(f)

with open("datasets/market_prices.json", "r", encoding="utf-8") as f:
    MARKET_PRICES = json.load(f)

with open("datasets/pest_control.json", "r", encoding="utf-8") as f:
    PEST_DATA = json.load(f)

with open("datasets/fertilizer_guidance.json", "r", encoding="utf-8") as f:
    FERTILIZER_DATA = json.load(f)

# ------------------- WEATHER API LOGIC -------------------
WEATHER_API_KEY ="6afa4533cf7fe411ec73ff6bfc949475"

SUPPORTED_CITIES = [
    "nagpur", "pune", "mumbai", "kolhapur",
    "nashik", "aurangabad", "solapur",
    "latur", "amravati", "wardha"
]

def get_weather_response(message):
    msg = message.lower()

    weather_keywords = ["weather", "rain", "temperature", "climate", "forecast"]

    if any(word in msg for word in weather_keywords):

        city = None
        for c in SUPPORTED_CITIES:
            if c in msg:
                city = c.capitalize()
                break

        if city is None:
            city = "Nagpur"  # default

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )

        try:
            response = requests.get(url)
            data = response.json()

            if data.get("cod") != 200:
                return f"Weather API Error: {data.get('message', 'Unknown error')}"

            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            condition = data["weather"][0]["description"]

            return (
                f"Weather Update for {city}:\n"
                f"Temperature: {temp}°C\n"
                f"Humidity: {humidity}%\n"
                f"Condition: {condition}"
            )

        except:
            return "Weather service is temporarily unavailable."

    return None


# ------------------- SMART MATCHING FUNCTION -------------------
def match_farmer_dataset(message):
    msg = message.lower()

    for category, items in FARMER_DATASET.items():
        for item in items:
            if "patterns" not in item:
                continue

            for pattern in item["patterns"]:
                pattern = pattern.lower()

                # extract important keywords (except common words)
                pattern_keywords = [w for w in pattern.split() if w not in ["crop", "for", "best", "in", "soil", "rain", "fertilizer"]]

                # check if any important keyword appears in the message
                for keyword in pattern_keywords:
                    if keyword in msg:
                        return random.choice(item["responses"])

                # full phrase match (for Hindi/Marathi)
                if pattern in msg:
                    return random.choice(item["responses"])

    return None
# ------------------- MARKET PRICE LOGIC (STEP-4) -------------------
def get_market_price(message):
    msg = message.lower()

    if "price" in msg or "rate" in msg or "market" in msg:
        for crop in MARKET_PRICES:
            if crop in msg:
                data = MARKET_PRICES[crop]
                return f"{crop.capitalize()} Market Price:\n{data['price']}\n{data['market']}"

    return None

# ------------------- PEST CONTROL LOGIC --------------------
def get_pest_control(message):
    msg = message.lower()

    if "pest" in msg or "insect" in msg or "disease" in msg:
        for crop, pests in PEST_DATA.items():
            if crop in msg:
                response = f"{crop.capitalize()} Pest Control:\n"
                for p in pests:
                    response += (
                        f"- Pest: {p['pest']}\n"
                        f"  Symptoms: {p['symptoms']}\n"
                        f"  Control: {p['control']}\n\n"
                    )
                return response.strip()
    return None

# ------------------- FERTILIZER LOGIC -------------------
def get_fertilizer_guidance(message):
    msg = message.lower()

    if "fertilizer" in msg or "manure" in msg or "npk" in msg:
        for crop, data in FERTILIZER_DATA.items():
            if crop in msg:
                return (
                    f"{crop.capitalize()} Fertilizer Guidance:\n"
                    f"Basal Dose: {data['basal']}\n"
                    f"Top Dressing: {data['top_dressing']}\n"
                    f"Micronutrients: {data['micronutrients']}"
                )
    return None
   

# ------------------- BOT RESPONSE LOGIC -------------------
def get_bot_response(message):
    
      
    # Weather check
    weather_reply = get_weather_response(message)
    if weather_reply:
        return weather_reply
    
     # fertilizer check
    fertilizer_reply = get_fertilizer_guidance(message)
    if fertilizer_reply:
     return fertilizer_reply
 
    # Pest control check
    pest_reply = get_pest_control(message)
    if pest_reply:
     return pest_reply

    # CHECK MARKET PRICE FIRST
    price_reply = get_market_price(message)
    if price_reply:
        return price_reply
    
   
    # 🔽 EXISTING LOGIC (UNCHANGED)
    dataset_reply = match_farmer_dataset(message)
    if dataset_reply:
        return dataset_reply

    return "Sorry, I didn't understand. Please ask about crops, pests, soil, fertilizer, rainfall, etc."


# ------------------- ROUTES -------------------
@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/get", methods=["POST"])
def get_response():
    data = request.get_json()
    user_message = data.get("message", "")

    reply = get_bot_response(user_message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
