from flask import Flask, request
import requests
import time
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

API_URL = "https://shopgmail9999.com/api/BuyGmail/GetstockGmail?apikey=183ac98abf6442e18d405d5dc233b793&id=8"

BOT_TOKEN = "8616807868:AAGjpIo8xkYySM3QMJ4lEdfAZ70FOisAkoQ"
CHAT_IDS = [8554175804, 5696721438]

last_stock = 0
current_stock = 0

# Giờ Việt Nam (UTC+7)
VN_TZ = timezone(timedelta(hours=7))

def vn_time():
    return datetime.now(VN_TZ).strftime("%H:%M:%S %d/%m/%Y")

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
        text = msg.get("text", "").strip()

        if text == "/start":
            intro = f"""<b>👋 Xin chào! Đây là Bot Monitor Stock Gmail</b>

📧 <b>Gmail 10 Phút - VERIFY ACC GAME</b>

✅ Bot sẽ tự động thông báo ngay khi stock > 0
🔄 Kiểm tra stock mỗi 1 phút

📌 Các lệnh nhanh:
• /stock  → Xem stock hiện tại
• /check  → Check stock ngay
• /status → Xem trạng thái bot
• /test   → Test thông báo

🕒 Thời gian hiển thị theo giờ Việt Nam
Bot đang chạy ổn định trên Render + cron-job.org"""
            send_telegram(chat_id, intro)

        elif text in ["/stock", "/check"]:
            try:
                r = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
                stock = r.json().get("data", {}).get("stock", 0)
                current_stock = stock

                reply = f"""📦 <b>Stock hiện tại</b>

Gmail 10 Phút - VERIFY ACC GAME
Stock: <b>{stock}</b>
⏰ {vn_time()}"""
                send_telegram(chat_id, reply)
            except:
                send_telegram(chat_id, "❌ Lỗi khi lấy stock, thử lại sau")

        elif text == "/status":
            send_telegram(chat_id, f"✅ Bot đang chạy bình thường\nStock hiện tại: <b>{current_stock}</b>\n⏰ {vn_time()}")

        elif text == "/test":
            send_telegram(chat_id, f"🔥 Test thông báo thành công\n⏰ {vn_time()}")

    return "OK", 200

@app.route('/set_webhook')
def set_webhook():
    webhook_url = "https://gmail-stock-cron.onrender.com/webhook"
    # Set webhook
    r1 = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", json={"url": webhook_url})
    # Set menu
    commands = [
        {"command": "start", "description": "Bắt đầu & hướng dẫn"},
        {"command": "stock", "description": "Xem stock hiện tại"},
        {"command": "check", "description": "Check stock ngay"},
        {"command": "status", "description": "Xem trạng thái bot"},
        {"command": "test", "description": "Test thông báo"}
    ]
    r2 = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands", json={"commands": commands})

    return f"✅ Setup webhook + menu thành công!", 200

@app.route('/check')
def background_check():
    global last_stock, current_stock
    try:
        r = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        stock = r.json().get("data", {}).get("stock", 0)
        current_stock = stock

        if stock > 0 and last_stock <= 0:
            message = f"""<b>✅ STOCK ĐÃ CÓ HÀNG!</b>

Gmail 10 Phút - VERIFY ACC GAME
Stock hiện tại: <b>{stock}</b>
⏰ {vn_time()}"""
            broadcast(message)
            print(f"✅ GỬI THÔNG BÁO - Stock = {stock} lúc {vn_time()}")

        else:
            print(f"Stock hiện tại: {stock} - {vn_time()}")

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
    return "<h1>✅ Bot Telegram Stock Gmail (giờ VN) đang chạy tốt!<br><a href='/set_webhook'>🔧 Set webhook + menu</a></h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
