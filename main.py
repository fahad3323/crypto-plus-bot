import time
import telebot
import threading
import requests
import json
import os

TOKEN = "7839759534:AAEigi9npxA-FLq4Hp2SvpzLfZLE2xpSRdw"
bot = telebot.TeleBot(TOKEN)
SUBSCRIBERS_FILE = "subscribers.json"
admin_id = 610937553

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_subscribers():
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subscribers), f)

subscribers = load_subscribers()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id not in subscribers:
        subscribers.add(user_id)
        save_subscribers()

    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("أفضل العملات الآن", callback_data="show_top25")
    btn2 = telebot.types.InlineKeyboardButton("أسوأ العملات الآن", callback_data="show_worst25")
    markup.add(btn1, btn2)

    bot.send_message(user_id, "أهلاً بك في بوت Crypto Plus.\nتم تسجيلك بنجاح لاستقبال أفضل العملات تلقائيًا كل 6 ساعات.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "show_top25":
        message = get_top_25_gainers()
        bot.send_message(call.message.chat.id, message)
    elif call.data == "show_worst25":
        message = get_top_25_losers()
        bot.send_message(call.message.chat.id, message)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id != admin_id:
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.reply_to(message, "اكتب الرسالة بعد الأمر مباشرة.")
        return
    count = 0
    for user_id in subscribers:
        try:
            bot.send_message(user_id, text)
            count += 1
        except:
            continue
    bot.reply_to(message, f"تم إرسال الرسالة إلى {count} مشترك.")

def get_top_25_gainers():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()
    filtered = [x for x in data if x['symbol'].endswith('USDT') and not x['symbol'].endswith('BUSD')]
    sorted_data = sorted(filtered, key=lambda x: float(x['priceChangePercent']), reverse=True)
    top_25 = sorted_data[:25]

    result = "أعلى 25 عملة من حيث الارتفاع (آخر 24 ساعة):\n\n"
    for i, coin in enumerate(top_25, 1):
        symbol = coin['symbol']
        change = float(coin['priceChangePercent'])
        price = float(coin['lastPrice'])
        result += f"{i}. {symbol}: +{change:.2f}% | السعر: ${price:.4f}\n"
    return result

def get_top_25_losers():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()
    filtered = [x for x in data if x['symbol'].endswith('USDT') and not x['symbol'].endswith('BUSD')]
    sorted_data = sorted(filtered, key=lambda x: float(x['priceChangePercent']))
    worst_25 = sorted_data[:25]

    result = "أسوأ 25 عملة من حيث الهبوط (آخر 24 ساعة):\n\n"
    for i, coin in enumerate(worst_25, 1):
        symbol = coin['symbol']
        change = float(coin['priceChangePercent'])
        price = float(coin['lastPrice'])
        result += f"{i}. {symbol}: {change:.2f}% | السعر: ${price:.4f}\n"
    return result

def auto_send_updates():
    while True:
        message = get_top_25_gainers()
        for user_id in subscribers:
            try:
                bot.send_message(user_id, message)
            except:
                continue
        time.sleep(6 * 60 * 60)

threading.Thread(target=auto_send_updates).start()
bot.infinity_polling()
