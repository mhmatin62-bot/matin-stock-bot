import telebot
import requests
import time

TOKEN = "8949265474:AAF03uLgyIjxxqZdyYBSOLV4-5g1kEJNlsE"

bot = telebot.TeleBot(TOKEN)

def get_market_data():
    try:
        url = "http://cdn.tsetmc.com/api/ClosePrice/Market/GetAllClosingPrice/0"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        response = requests.get(url, timeout=15, headers=headers)
        
        if response.status_code != 200:
            print(f"Status code: {response.status_code}")
            return None
            
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
        
        print(f"✅ Received {len(stocks)} stocks")
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
                is_option = 'AP' in symbol or 'اختیار' in symbol
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
    msg = bot.reply_to(message, "🔄 Fetching data...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.edit_message_text("❌ Error fetching data. Please try again.", msg.chat.id, msg.message_id)
        return
    
    signals = generate_signals(stocks)
    if not signals:
        bot.edit_message_text("⛔ No buy signals found today.", msg.chat.id, msg.message_id)
        return
    
    response = "📊 **Buy Signals Today:**\n\n"
    for s in signals:
        response += f"✅ {s['symbol']} ({s['type']})\n"
        response += f"   Price: {s['price']:,.0f} Toman\n"
        response += f"   Change: {s['change']:+,.2f}%\n"
        response += f"   Volume: {s['volume']:,.0f}\n\n"
    
    bot.edit_message_text(response, msg.chat.id, msg.message_id)

@bot.message_handler(commands=['top'])
def get_top(message):
    msg = bot.reply_to(message, "🔄 Fetching data...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.edit_message_text("❌ Error fetching data.", msg.chat.id, msg.message_id)
        return
    
    try:
        top = sorted(stocks, key=lambda x: x['volume'], reverse=True)[:5]
        response = "🏆 **Top 5 Stocks Today:**\n\n"
        for item in top:
            response += f"• {item['symbol']}\n"
            response += f"  Price: {item['price']:,.0f} Toman\n"
            response += f"  Volume: {item['volume']:,.0f}\n\n"
        bot.edit_message_text(response, msg.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", msg.chat.id, msg.message_id)

@bot.message_handler(commands=['option'])
def get_options(message):
    msg = bot.reply_to(message, "🔄 Searching options...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.edit_message_text("❌ Error fetching data.", msg.chat.id, msg.message_id)
        return
    
    try:
        options = [x for x in stocks if 'AP' in x['symbol'] or 'اختیار' in x['symbol']]
        if not options:
            bot.edit_message_text("⛔ No option contracts found today.", msg.chat.id, msg.message_id)
            return
        
        top_options = sorted(options, key=lambda x: x['volume'], reverse=True)[:5]
        response = "📈 **Option Contracts Today:**\n\n"
        for item in top_options:
            response += f"• {item['symbol']}\n"
            response += f"  Price: {item['price']:,.0f} Toman\n"
            response += f"  Change: {item['change']:+,.2f}%\n"
            response += f"  Volume: {item['volume']:,.0f}\n\n"
        bot.edit_message_text(response, msg.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", msg.chat.id, msg.message_id)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
        "📚 **Help:**\n\n"
        "🔍 Buy Signal Criteria:\n"
        "• Volume > 5 Billion Toman\n"
        "• Positive price change\n\n"
        "⚠️ **Note:** Signals are for informational purposes only."
    )

if __name__ == "__main__":
    print("✅ Bot is running...")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
