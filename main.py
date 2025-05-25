import time
import telebot
import threading
import requests

TOKEN = "7839759534:AAEigi9npxA-FLq4Hp2SvpzLfZLE2xpSRdw"
bot = telebot.TeleBot(TOKEN)

subscribers = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    subscribers.add(user_id)
    bot.reply_to(message, "أهلاً بك في بوت Crypto Plus. يتم إرسال أفضل 25 عملة مرتفعة تلقائيًا كل 6 ساعات.")

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
        result += f"{i}. {symbol}: +{change:.2f}% | Price: ${price:.4f}\n"

    return result

def auto_send_updates():
    while True:
        message = get_top_25_gainers()
        for user_id in subscribers:
            try:
                bot.send_message(user_id, message)
            except:
                continue
        time.sleep(6 * 60 * 60)  # كل 6 ساعات

threading.Thread(target=auto_send_updates).start()
bot.infinity_polling()
