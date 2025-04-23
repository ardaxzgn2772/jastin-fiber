from flask import Flask, request
import requests
import datetime
import os

app = Flask(__name__)

# .envなどから取得するようにすると安全（ここは直書き例）
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1351035408452157481/morpMb-ZPX1LgT3169n5yhFbm-pvsPVGBIravlKFHxgu2sNfo2yDE7R72QOhYxIVZd8f"
IPINFO_TOKEN = "dce1ce98e3367a"

# IP取得
def get_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr

# IPの位置情報を取得
def get_ip_info(ip):
    try:
        res = requests.get(f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}", timeout=3)
        return res.json()
    except Exception as e:
        print("IP情報取得失敗:", e)
        return {}

# ローカルにログを保存
def log_locally(ip, ua, region, country, city):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{time}] IP: {ip}, 地域: {region}, 国: {country}, 都市: {city}, UA: {ua}\n"
    with open("ip_log.txt", "a", encoding='utf-8') as f:
        f.write(log_entry)
    print(log_entry.strip())

# DiscordにEmbed形式で送信
def send_to_discord(ip, ua, region, country, city):
    embed = {
        "title": "📡 新しいアクセス検出",
        "color": 0x00FFAA,
        "fields": [
            {"name": "IPアドレス", "value": f"`{ip}`", "inline": False},
            {"name": "国・地域", "value": f"{country} / {region}", "inline": True},
            {"name": "都市", "value": city, "inline": True},
            {"name": "User-Agent", "value": ua, "inline": False}
        ],
        "footer": {"text": "IP Logger System"},
    }

    payload = {
        "username": "IP Logger Bot",
        "embeds": [embed]
    }

    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=3)
        if res.status_code != 204:
            print("⚠️ Discord送信失敗:", res.text)
    except Exception as e:
        print("❌ Discord通信エラー:", e)

@app.route('/')
def index():
    ip = get_ip()
    ua = request.headers.get('User-Agent', '不明')
    geo = get_ip_info(ip)

    country = geo.get("country", "不明")
    region = geo.get("region", "不明")
    city = geo.get("city", "不明")

    log_locally(ip, ua, region, country, city)
    send_to_discord(ip, ua, region, country, city)

    return "<h1>ようこそ</h1><p>アクセスが記録されました。</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # ←これ大事！

