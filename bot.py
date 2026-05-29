import os
import telebot
import json
from flask import Flask, request
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

clients = {}
logged_users = {}

# -----------------------------
# WEBHOOK
# -----------------------------

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_json()
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def home():
    return "Bot is running!"


# -----------------------------
# START
# -----------------------------

@bot.message_handler(commands=['start'])
def start(message):

    code = message.text.split()[-1] if len(message.text.split()) > 1 else None

    if code and code in clients:

        client = clients[code]

        logged_users[message.chat.id] = code

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        btn1 = types.KeyboardButton("👤 اطلاعات من")
        btn2 = types.KeyboardButton("💰 تعرفه جلسه")
        btn3 = types.KeyboardButton("📞 شماره تماس")
        btn4 = types.KeyboardButton("📝 یادداشت")

        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        markup.add(btn4)

        text = f"""
👋 سلام {client.get('name', '')}

به پنل شخصی خود خوش آمدید.
"""

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=markup
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ کد معتبر نیست\n\n/start [کد]"
        )


# -----------------------------
# INFO
# -----------------------------

@bot.message_handler(func=lambda m: m.text == "👤 اطلاعات من")
def info_handler(message):

    if message.chat.id not in logged_users:
        bot.reply_to(message, "ابتدا وارد شوید")
        return

    code = logged_users[message.chat.id]

    client = clients[code]

    text = f"""
👤 نام:
{client.get('name', '-')}

🆔 کد:
{client.get('id', '-')}

📞 تلفن:
{client.get('phone', '-')}

💰 تعرفه جلسه:
{client.get('hourlyRate', 0):,} تومان
"""

    bot.reply_to(message, text)


# -----------------------------
# SESSION PRICE
# -----------------------------

@bot.message_handler(func=lambda m: m.text == "💰 تعرفه جلسه")
def rate_handler(message):

    if message.chat.id not in logged_users:
        bot.reply_to(message, "ابتدا وارد شوید")
        return

    code = logged_users[message.chat.id]

    client = clients[code]

    text = f"""
💰 تعرفه هر جلسه:

{client.get('hourlyRate', 0):,} تومان
"""

    bot.reply_to(message, text)


# -----------------------------
# PHONE
# -----------------------------

@bot.message_handler(func=lambda m: m.text == "📞 شماره تماس")
def phone_handler(message):

    if message.chat.id not in logged_users:
        bot.reply_to(message, "ابتدا وارد شوید")
        return

    code = logged_users[message.chat.id]

    client = clients[code]

    phone = client.get("phone", "")

    if not phone:
        phone = "ثبت نشده"

    bot.reply_to(
        message,
        f"📞 شماره تماس:\n{phone}"
    )


# -----------------------------
# NOTES
# -----------------------------

@bot.message_handler(func=lambda m: m.text == "📝 یادداشت")
def notes_handler(message):

    if message.chat.id not in logged_users:
        bot.reply_to(message, "ابتدا وارد شوید")
        return

    code = logged_users[message.chat.id]

    client = clients[code]

    notes = client.get("notes", "")

    if not notes:
        notes = "یادداشتی ثبت نشده"

    bot.reply_to(
        message,
        f"📝 یادداشت:\n{notes}"
    )


# -----------------------------
# JSON BACKUP
# -----------------------------

@bot.message_handler(content_types=['document'])
def handle_backup(message):

    try:

        file_info = bot.get_file(
            message.document.file_id
        )

        downloaded = bot.download_file(
            file_info.file_path
        )

        data = json.loads(
            downloaded.decode("utf-8")
        )

        global clients

        clients = {
            c['id']: c
            for c in data.get('clients', [])
        }

        bot.reply_to(
            message,
            f"""
✅ فایل با موفقیت بارگذاری شد

👥 تعداد مراجعین:
{len(clients)}
"""
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ خطا:\n{str(e)}"
        )


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":

    bot.remove_webhook()

    render_url = os.environ.get(
        "RENDER_EXTERNAL_URL"
    )

    bot.set_webhook(
        url=f"{render_url}/{TOKEN}"
    )

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
