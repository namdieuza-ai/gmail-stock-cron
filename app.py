from flask import Flask
import requests
import time
import os

app = Flask(__name__)

# ←←← ĐÃ SỬA ID THÀNH 8
API_URL = "https://shopgmail9999.com/api/BuyGmail/GetstockGmail?apikey=183ac98abf6442e18d405d5dc233b793&id=8"
NTFY_TOPIC = "gmail-stock-9999"   # ←←← THAY BẰNG TÊN TOPIC NTFY CỦA BẠN

last_stock = 0

@app.route('/check')
def check_stock():
    global last_stock
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(API_URL, headers=headers, timeout=15)
        
        print(f"Status: {r.status_code} | Response: {r.text[:300]}")

        if r.status_code != 200 or not r.text.strip().startswith('{'):
            print("⚠️ API không trả JSON")
            return "API error", 200

        data = r.json()
        stock = data.get("data", {}).get("stock", 0)

        if stock > 0 and last_stock <= 0:
            message = f"""✅ STOCK ĐÃ CÓ HÀNG!
Gmail 10 Phút - VERIFY ACC GAME
Stock hiện tại: {stock}
⏰ {time.strftime("%H:%M:%S %d/%m/%Y")}"""

            requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                headers={"Title": "🔥 Gmail Stock Alert!", "Priority": "high", "Tags": "rocket,mail"},
                data=message
            )
            print(f"✅ GỬI NTFY - Stock = {stock}")

        else:
            print(f"📦 Stock hiện tại: {stock}")

        # Reset logic
        if stock == 0:
            last_stock = 0
        else:
            last_stock = stock

        return f"OK - Stock: {stock}", 200

    except Exception as e:
        print("❌ Lỗi:", str(e))
        return "ERROR", 500

@app.route('/')
def home():
    return "<h1>✅ Gmail Stock Monitor đang chạy!<br>Link cron: /check</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
