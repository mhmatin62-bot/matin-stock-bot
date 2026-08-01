import telebot
import time

TOKEN = "8949265474:AAF03uLgyIjxxqZdyYBSOLV4-5g1kEJNlsE"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Bot is working!")

@bot.message_handler(commands=['test'])
def test(message):
    bot.reply_to(message, "✅ Test successful!")

@bot.message_handler(commands=['signals'])
def signals(message):
    bot.reply_to(message, "📊 Signal: FOLAD - 5000 Toman")

@bot.message_handler(commands=['top'])
def top(message):
    bot.reply_to(message, "🏆 Top: 1. FOLAD 2. KHODRO 3. SHESTA")

@bot.message_handler(commands=['option'])
def option(message):
    bot.reply_to(message, "📈 Option: FOLAD-AP-1401")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Commands: /start /signals /top /option /test")

print("✅ Bot started!")

while True:
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
