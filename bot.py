import telebot
import requests
import time

TOKEN = "8949265474:AAF03uLgyIjxxqZdyYBSOLV4-5g1kEJNlsE"

bot = telebot.TeleBot(TOKEN)

def get_market_data():
    try:
        url = "http://cdn.tsetmc.com/api/ClosePrice/Market/GetAllClosingPrice/0"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        stocks = []
        for item in data['closingPrice']:
            symbol = item['instrument']['lVal30']
            price = item.get('pTitran', 0) / 10
            volume = item.get('qTitran', 0)
            change = item.get('pDrCotVal', 0)
            
            stocks.append({
                'symbol': symbol,
                'price': price,
                'volume': volume,
                'change': change
            })
        return stocks
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_signals(stocks):
    signals = []
    if not stocks:
        return []
    
    for item in stocks:
        try:
            price = float(item.get('price', 0))
            volume = float(item.get('volume', 0))
            change = float(item.get('change', 0))
            symbol = str(item.get('symbol', ''))
            
            if volume > 5000000000 and change > 0 and price > 0:
                is_option = 'AP' in symbol
                signals.append({
                    'symbol': symbol,
                    'price': price,
                    'change': change,
                    'volume': volume,
                    'type': 'Option' if is_option else 'Stock'
                })
        except:
            continue
    
    signals = sorted(signals, key=lambda x: x['change'], reverse=True)
    return signals[:10]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        "🤖 Stock Signal Bot\n\n"
        "Commands:\n"
        "/signals - Buy signals\n"
        "/top - Top 5 stocks\n"
        "/option - Option contracts\n"
        "/help - Help"
    )

@bot.message_handler(commands=['signals'])
def get_signals(message):
    bot.reply_to(message, "🔄 Fetching data...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.reply_to(message, "❌ Error fetching data.")
        return
    
    signals = generate_signals(stocks)
    if not signals:
        bot.reply_to(message, "⛔ No signals today.")
        return
    
    response = "📊 Buy Signals:\n\n"
    for s in signals:
        response += f"✅ {s['symbol']} ({s['type']})\n"
        response += f"   Price: {s['price']:,.0f} Toman\n"
        response += f"   Change: {s['change']:+,.2f}%\n"
        response += f"   Volume: {s['volume']:,.0f}\n\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['top'])
def get_top(message):
    bot.reply_to(message, "🔄 Fetching data...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.reply_to(message, "❌ Error.")
        return
    
    try:
        top = sorted(stocks, key=lambda x: x['volume'], reverse=True)[:5]
        response = "🏆 Top 5 Stocks:\n\n"
        for item in top:
            response += f"• {item['symbol']}\n"
            response += f"  Price: {item['price']:,.0f} Toman\n"
            response += f"  Volume: {item['volume']:,.0f}\n\n"
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['option'])
def get_options(message):
    bot.reply_to(message, "🔄 Searching options...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.reply_to(message, "❌ Error.")
        return
    
    try:
        options = [x for x in stocks if 'AP' in x['symbol']]
        if not options:
            bot.reply_to(message, "⛔ No options today.")
            return
        
        top_options = sorted(options, key=lambda x: x['volume'], reverse=True)[:5]
        response = "📈 Option Contracts:\n\n"
        for item in top_options:
            response += f"• {item['symbol']}\n"
            response += f"  Price: {item['price']:,.0f} Toman\n"
            response += f"  Change: {item['change']:+,.2f}%\n"
            response += f"  Volume: {item['volume']:,.0f}\n\n"
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
        "📚 Help:\n\n"
        "Signal Criteria:\n"
        "• Volume > 5B Toman\n"
        "• Positive change\n\n"
        "⚠️ Informational only."
    )

if __name__ == "__main__":
    print("✅ Bot is running...")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
