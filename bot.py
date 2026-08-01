import telebot
import requests
import requests

TOKEN = "8949265474:AAF03uLgyIjxxqZdyYBSOLV4-5g"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Bot is working! Try /signals")

@bot.message_handler(commands=['signals'])
def get_signals(message):
    bot.reply_to(message, "📊 Test signal: فولاد - 5000 Toman")

@bot.message_handler(commands=['top'])
def get_top(message):
    bot.reply_to(message, "🏆 Test: 1. فولاد 2. خودرو 3. شستا")

@bot.message_handler(commands=['option'])
def get_options(message):
    bot.reply_to(message, "📈 Test option: فولاد-AP-1401")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Commands: /start /signals /top /option")

print("✅ Bot is starting...")

while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
