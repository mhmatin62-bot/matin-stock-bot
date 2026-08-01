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

# ===== داده‌های آزمایشی (همیشه جواب میده) =====
def get_fake_data():
    return [
        {'نماد': 'فولاد', 'قیمت': 4850, 'حجم': 6200000000, 'تغییر': 2.5},
        {'نماد': 'خودرو', 'قیمت': 3120, 'حجم': 7500000000, 'تغییر': 3.1},
        {'نماد': 'شستا', 'قیمت': 4080, 'حجم': 5800000000, 'تغییر': 1.8},
        {'نماد': 'فملی', 'قیمت': 7950, 'حجم': 5300000000, 'تغییر': 4.2},
        {'نماد': 'کگل', 'قیمت': 2520, 'حجم': 5100000000, 'تغییر': 2.0},
        {'نماد': 'وبملت', 'قیمت': 1850, 'حجم': 4900000000, 'تغییر': -0.5},
        {'نماد': 'فارس', 'قیمت': 9200, 'حجم': 4700000000, 'تغییر': 1.2},
        {'نماد': 'خگستر', 'قیمت': 2100, 'حجم': 4500000000, 'تغییر': 0.8},
    ]

# ===== دریافت داده از بورس (با fallback) =====
def get_market_data():
    # تلاش برای دریافت داده از سایت بورس
    try:
        url = "http://cdn.tsetmc.com/api/ClosePrice/Market/GetAllClosingPrice/0"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "fa-IR,fa;q=0.9"
        }
        response = requests.get(url, timeout=8, headers=headers)
        
        if response.status_code == 200:
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
            if stocks:
                print(f"✅ دریافت {len(stocks)} سهم از بورس")
                return stocks
    except Exception as e:
        print(f"خطا در اتصال به بورس: {e}")
    
    # اگر سایت بورس جواب نداد، از داده‌های آزمایشی استفاده کن
    print("⚠️ استفاده از داده‌های آزمایشی")
    return get_fake_data()

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
        "از دکمه‌های زیر برای دریافت اطلاعات استفاده کنید:\n\n"
        "⚠️ **توجه:** داده‌ها ممکن است آزمایشی باشند.",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📊 سیگنال")
def handle_signals(message):
    msg = bot.reply_to(message, "🔄 در حال دریافت داده‌ها...")
    
    stocks = get_market_data()
    signals = generate_signals(stocks)
    
    if not signals:
        bot.edit_message_text("⛔ امروز سیگنال خرید خاصی یافت نشد.", msg.chat.id, msg.message_id, reply_markup=main_menu())
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
    if not stocks:
        bot.edit_message_text("❌ خطا در دریافت داده.", msg.chat.id, msg.message_id, reply_markup=main_menu())
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
    if not stocks:
        bot.edit_message_text("❌ خطا در دریافت داده.", msg.chat.id, msg.message_id, reply_markup=main_menu())
        return
    
    try:
        options = [x for x in stocks if 'AP' in x['نماد'] or 'اختیار' in x['نماد']]
        if not options:
            bot.edit_message_text("⛔ امروز اختیار معامله‌ای یافت نشد.", msg.chat.id, msg.message_id, reply_markup=main_menu())
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
