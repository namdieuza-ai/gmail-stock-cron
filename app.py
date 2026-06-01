from flask import Flask, request
import requests
import time
import os

app = Flask(__name__)

API_URL = "https://shopgmail9999.com/api/BuyGmail/GetstockGmail?apikey=183ac98abf6442e18d405d5dc233b793&id=8"

BOT_TOKEN = "8616807868:AAGjpIo8xkYySM3QMJ4lEdfAZ70FOisAkoQ"
CHAT_IDS = [8554175804, 5696721438]   # 2 tài khoản nhận thông báo stock

last_stock = 0
current_stock = 0

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False

def broadcast(message):
    for cid in CHAT_IDS:
        send_telegram(cid, message)

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    global last_stock, current_stock
    update = request.json

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/stock" or text == "/check":
            try:
                r = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                stock = r.json().get("data", {}).get("stock", 0)
                current_stock = stock

                reply = f"""📦 <b>Stock hiện tại</b>

Gmail 10 Phút - VERIFY ACC GAME
Stock: <b>{stock}</b>
⏰ {time.strftime("%H:%M:%S %d/%m/%Y")}"""
                send_telegram(chat_id, reply)
            except:
                send_telegram(chat_id, "❌ Lỗi khi lấy stock")

        elif text == "/test":
            send_telegram(chat_id, f"🔥 Test thông báo - {time.strftime('%H:%M:%S')}")

        elif text == "/status":
            send_telegram(chat_id, f"✅ Monitor đang chạy bình thường\nStock hiện tại: {current_stock}")

    return "OK", 200

@app.route('/set_webhook')
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_url = "https://gmail-stock-cron.onrender.com/webhook"
    r = requests.post(url, json={"url": webhook_url})
    return f"Set webhook: {r.json()}", 200

@app.route('/check')
def check_stock():
    global last_stock, current_stock
    try:
        r = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        stock = r.json().get("data", {}).get("stock", 0)
        current_stock = stock

        if stock > 0 and last_stock <= 0:
            message = f"""<b>✅ STOCK ĐÃ CÓ HÀNG!</b>

Gmail 10 Phút - VERIFY ACC GAME
Stock hiện tại: <b>{stock}</b>
⏰ {time.strftime("%H:%M:%S %d/%m/%Y")}"""
            broadcast(message)
            print(f"✅ GỬI THÔNG BÁO - Stock = {stock}")

        else:
            print(f"Stock hiện tại: {stock}")

        if stock == 0:
            last_stock = 0
        else:
            last_stock = stock

        return "OK", 200
    except Exception as e:
        print(f"Lỗi: {e}")
        return "ERROR", 500

@app.route('/')
def home():
    return "<h1>✅ Bot Telegram đang chạy!<br>Webhook: /webhook | Set webhook: /set_webhook</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
