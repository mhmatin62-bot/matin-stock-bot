# -*- coding: utf-8 -*-
import telebot
import requests
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8949265474:AAF03uLgyIjxxqZdyYBSOLV4-5g1kEJNlsE"

bot = telebot.TeleBot(TOKEN)

# ===== دکمه‌های شیشه‌ای =====
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton("📊 سیگنال")
    btn2 = KeyboardButton("🏆 برتر")
    btn3 = KeyboardButton("📈 اختیار")
    btn4 = KeyboardButton("📚 راهنما")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# ===== دریافت داده از بورس =====
def get_market_data():
    try:
        url = "http://cdn.tsetmc.com/api/ClosePrice/Market/GetAllClosingPrice/0"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "fa-IR,fa;q=0.9"
        }
        response = requests.get(url, timeout=15, headers=headers)
        
        if response.status_code != 200:
            print(f"خطا: {response.status_code}")
            return None
            
        data = response.json()
        stocks = []
        
        for item in data['closingPrice']:
            symbol = item['instrument']['lVal30']
            price = item.get('pTitran', 0) / 10
            volume = item.get('qTitran', 0)
            change = item.get('pDrCotVal', 0)
            
            stocks.append({
                'نماد': symbol,
                'قیمت': price,
                'حجم': volume,
                'تغییر': change
            })
        
        print(f"✅ دریافت {len(stocks)} سهم")
        return stocks
        
    except Exception as e:
        print(f"خطا: {e}")
        return None

# ===== سیگنال‌ها =====
def generate_signals(stocks):
    signals = []
    if not stocks:
        return []
    
    for item in stocks:
        try:
            price = float(item.get('قیمت', 0))
            volume = float(item.get('حجم', 0))
            change = float(item.get('تغییر', 0))
            symbol = str(item.get('نماد', ''))
            
            if volume > 5000000000 and change > 0 and price > 0:
                is_option = 'AP' in symbol or 'اختیار' in symbol
                signals.append({
                    'نماد': symbol,
                    'قیمت': price,
                    'تغییر': change,
                    'حجم': volume,
                    'نوع': 'اختیار خرید' if is_option else 'سهام'
                })
        except:
            continue
    
    signals = sorted(signals, key=lambda x: x['تغییر'], reverse=True)
    return signals[:10]

# ===== دستورات ربات =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        "🤖 **ربات سیگنال بورس**\n\n"
        "👋 خوش آمدید!\n"
        "از دکمه‌های زیر برای دریافت اطلاعات استفاده کنید:",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📊 سیگنال")
def handle_signals(message):
    msg = bot.reply_to(message, "🔄 در حال دریافت داده‌ها...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.edit_message_text("❌ خطا در دریافت داده. لطفاً دوباره تلاش کنید.", msg.chat.id, msg.message_id)
        return
    
    signals = generate_signals(stocks)
    if not signals:
        bot.edit_message_text("⛔ امروز سیگنال خرید خاصی یافت نشد.", msg.chat.id, msg.message_id)
        return
    
    response = "📊 **سیگنال‌های خرید امروز:**\n\n"
    for s in signals:
        response += f"✅ {s['نماد']} ({s['نوع']})\n"
        response += f"   قیمت: {s['قیمت']:,.0f} تومان\n"
        response += f"   تغییر: {s['تغییر']:+,.2f}%\n"
        response += f"   حجم: {s['حجم']:,.0f}\n\n"
    
    bot.edit_message_text(response, msg.chat.id, msg.message_id, reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🏆 برتر")
def handle_top(message):
    msg = bot.reply_to(message, "🔄 در حال دریافت داده‌ها...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.edit_message_text("❌ خطا در دریافت داده.", msg.chat.id, msg.message_id)
        return
    
    try:
        top = sorted(stocks, key=lambda x: x['حجم'], reverse=True)[:5]
        response = "🏆 **۵ سهام پرمعامله امروز:**\n\n"
        for item in top:
            response += f"• {item['نماد']}\n"
            response += f"  قیمت: {item['قیمت']:,.0f} تومان\n"
            response += f"  حجم: {item['حجم']:,.0f}\n\n"
        bot.edit_message_text(response, msg.chat.id, msg.message_id, reply_markup=main_menu())
    except Exception as e:
        bot.edit_message_text(f"❌ خطا: {e}", msg.chat.id, msg.message_id, reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📈 اختیار")
def handle_options(message):
    msg = bot.reply_to(message, "🔄 در حال جستجوی اختیارها...")
    
    stocks = get_market_data()
    if stocks is None:
        bot.edit_message_text("❌ خطا در دریافت داده.", msg.chat.id, msg.message_id)
        return
    
    try:
        options = [x for x in stocks if 'AP' in x['نماد'] or 'اختیار' in x['نماد']]
        if not options:
            bot.edit_message_text("⛔ امروز اختیار معامله‌ای یافت نشد.", msg.chat.id, msg.message_id)
            return
        
        top_options = sorted(options, key=lambda x: x['حجم'], reverse=True)[:5]
        response = "📈 **اختیارهای خرید امروز:**\n\n"
        for item in top_options:
            response += f"• {item['نماد']}\n"
            response += f"  قیمت: {item['قیمت']:,.0f} تومان\n"
            response += f"  تغییر: {item['تغییر']:+,.2f}%\n"
            response += f"  حجم: {item['حجم']:,.0f}\n\n"
        bot.edit_message_text(response, msg.chat.id, msg.message_id, reply_markup=main_menu())
    except Exception as e:
        bot.edit_message_text(f"❌ خطا: {e}", msg.chat.id, msg.message_id, reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "📚 راهنما")
def handle_help(message):
    bot.reply_to(message,
        "📚 **راهنما:**\n\n"
        "🔍 معیارهای سیگنال خرید:\n"
        "• حجم معاملات بالای ۵ میلیارد تومان\n"
        "• تغییر قیمت مثبت\n\n"
        "📋 **دستورات:**\n"
        "📊 سیگنال - دریافت سیگنال‌های خرید\n"
        "🏆 برتر - ۵ سهام پرمعامله\n"
        "📈 اختیار - اختیارهای خرید\n"
        "📚 راهنما - این راهنما\n\n"
        "⚠️ **توجه:** سیگنال‌ها فقط اطلاع‌رسانی هستند.",
        reply_markup=main_menu()
    )

# ===== اجرا =====
if __name__ == "__main__":
    print("✅ ربات روشن شد!")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(5)
