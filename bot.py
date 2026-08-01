import telebot

TOKEN = "8949265474:AAF03uLgyIjxxqZdyYBSOLV4-5g"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ ربات کار میکند!")

@bot.message_handler(commands=['test'])
def test(message):
    bot.reply_to(message, "✅ تست موفق!")

print("✅ ربات روشن شد!")

while True:
    try:
        bot.infinity_polling()
    except:
        pass
