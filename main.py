
import time
import telebot
import threading

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت Crypto Plus!")

def run_bot():
    bot.infinity_polling()

def repeat_task():
    while True:
        # هنا تقدر تضيف كود التحديث كل 6 ساعات لاحقًا
        time.sleep(6 * 60 * 60)

threading.Thread(target=run_bot).start()
threading.Thread(target=repeat_task).start()
