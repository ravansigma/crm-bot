import os
import telebot
import json
from flask import Flask, request

TOKEN = "8862296016:AAFDKmHsoMnWdD2D20QYi3BkAknvWPw7i0A"

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

clients = {}

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.Update.de_json(request.get_json())])
    return "OK"

@bot.message_handler(commands=['start'])
def start(message):
    code = message.text.split()[-1] if len(message.text.split()) > 1 else None
    
    if code and code in clients:
        client = clients[code]
        text = f"👋 سلام {client['name']}!\n\n"
        text += f"📊 موجودی: {client.get('balance', 0):,} تومان\n"
        text += f"📅 آخرین جلسه: {client.get('lastSession', '-')}\n"
        text += f"🔢 کد شما: {code}"
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "لطفاً کد مراجعه رو وارد کنید:\n/start [کد]")

@bot.message_handler(content_types=['document'])
def handle_backup(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        data = json.loads(downloaded)
        
        global clients
        clients = {c['id']: c for c in data.get('clients', [])}
        
        bot.reply_to(message, f"✅ پشتیبانی ذخیره شد!\nتعداد مراجعین: {len(clients)}")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا: {str(e)}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get('RENDER_EXTERNAL_URL') + f"/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))