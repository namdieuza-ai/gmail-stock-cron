from flask import Flask
import requests
import time
import os

app = Flask(__name__)

API_URL = "https://shopgmail9999.com/api/BuyGmail/GetstockGmail?apikey=183ac98abf6442e18d405d5dc233b793&id=8"
NTFY_TOPIC = "gmail-stock-9999"   # ← Phải đúng y chang dòng này

last_stock = 0

def send_to_ntfy(message, title="Gmail Stock Alert!"):
    try:
        r = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            headers={
                "Title": title,
                "Priority": "high",
                "Tags": "rocket,mail",
                "Content-Type": "text/plain; charset=utf-8"
            },
            data=message,
            timeout=10
        )
        print(f"NTFY RESPONSE → Status: {r.status_code} | Text: {r.text[:200]}")
        return r.status_code == 200
    except Exception as e:
        print(f"NTFY ERROR: {e}")
        return False

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

            success = send_to_ntfy(message)
            if success:
                print(f"✅ GỬI NTFY THÀNH CÔNG - Stock = {stock}")
            else:
                print(f"❌ GỬI NTFY THẤT BẠI - Stock = {stock}")

        else:
            print(f"Stock hiện tại: {stock}")

        if stock == 0:
            last_stock = 0
        else:
            last_stock = stock

        return f"OK - Stock: {stock}", 200

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return "ERROR", 500

@app.route('/test')
def test_ntfy():
    """Test gửi thông báo thủ công"""
    message = "🔥 TEST THÔNG BÁO TỪ RENDER - " + time.strftime("%H:%M:%S")
    success = send_to_ntfy(message, title="Test NTFY")
    return f"Test gửi NTFY: {'Thành công' if success else 'Thất bại'}", 200

@app.route('/')
def home():
    return "<h1>✅ Gmail Stock Monitor đang chạy!<br>Test: <a href='/test'>/test</a> | Check: /check</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
