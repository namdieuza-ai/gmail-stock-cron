from flask import Flask
import requests
import time
import os

app = Flask(__name__)

API_URL = "https://shopgmail9999.com/api/BuyGmail/GetstockGmail?apikey=183ac98abf6442e18d405d5dc233b793&id=8"

BOT_TOKEN = "8616807868:AAGjpIo8xkYySM3QMJ4lEdfAZ70FOisAkoQ"
CHAT_IDS = [8554175804, 5696721438]   # ← Đã thêm 2 ID

last_stock = 0

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    success_count = 0
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code == 200:
                success_count += 1
                print(f"✅ Gửi thành công cho chat_id {chat_id}")
            else:
                print(f"❌ Gửi thất bại cho chat_id {chat_id} - {r.text}")
        except Exception as e:
            print(f"❌ Lỗi gửi cho chat_id {chat_id}: {e}")
    return success_count > 0

@app.route('/check')
def check_stock():
    global last_stock
    try:
        r = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        stock = r.json().get("data", {}).get("stock", 0)

        if stock > 0 and last_stock <= 0:
            message = f"""<b>✅ STOCK ĐÃ CÓ HÀNG!</b>

Gmail 10 Phút - VERIFY ACC GAME
Stock hiện tại: <b>{stock}</b>
⏰ {time.strftime("%H:%M:%S %d/%m/%Y")}"""

            if send_telegram(message):
                print(f"✅ GỬI TELEGRAM THÀNH CÔNG - Stock = {stock}")
            else:
                print(f"❌ GỬI TELEGRAM THẤT BẠI - Stock = {stock}")

        else:
            print(f"Stock hiện tại: {stock}")

        if stock == 0:
            last_stock = 0
        else:
            last_stock = stock

        return f"OK - Stock: {stock}", 200

    except Exception as e:
        print(f"Lỗi: {e}")
        return "ERROR", 500

@app.route('/test')
def test_telegram():
    message = "🔥 TEST THÔNG BÁO TỪ RENDER - " + time.strftime("%H:%M:%S")
    success = send_telegram(message)
    return f"Test Telegram: {'Thành công' if success else 'Thất bại'}", 200

@app.route('/')
def home():
    return "<h1>✅ Gmail Stock Monitor (Telegram - 2 tài khoản) đang chạy!<br>Test: <a href='/test'>/test</a> | Check: /check</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
