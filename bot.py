import telebot
from telebot import types
import time
import sqlite3
import json

# الإعدادات الملكية
API_TOKEN = '8695352652:AAE4eed89NQYWg2ycbK8wcWpuY5tQQ-APPY'
bot = telebot.TeleBot(API_TOKEN)
ADMIN_ID = 8421694319 # معرف السلطانة زينب

# روابط الهوية البصرية
IMAGES = {
    "MAIN": "https://r2.erweima.ai/i/1000034570.png",
    "BORDJ": "https://r2.erweima.ai/i/1000034589.png",
    "CONSTANTINE": "https://r2.erweima.ai/i/1000034588.png",
    "GHARDAIA": "https://r2.erweima.ai/i/1000034590.png",
    "TLEMCEN": "https://r2.erweima.ai/i/1000034592.png"
}

MARKET_DATA = {
    "برج بوعريريج": {"item": "القمح الذهبي", "buy": 100, "sell": 180, "img": IMAGES["BORDJ"]},
    "قسنطينة": {"item": "نحاس القصبة", "buy": 800, "sell": 1200, "img": IMAGES["CONSTANTINE"]},
    "غرداية": {"item": "الزرابي الميزابية", "buy": 300, "sell": 500, "img": IMAGES["GHARDAIA"]},
    "تلمسان": {"item": "الحرير التلمساني", "buy": 600, "sell": 950, "img": IMAGES["TLEMCEN"]}
}

# --- إدارة قاعدة البيانات (SQL) ---
def init_db():
    conn = sqlite3.connect('atlas_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, balance INTEGER, level INTEGER, inv TEXT)''')
    conn.commit()
    conn.close()

def get_player(uid):
    conn = sqlite3.connect('atlas_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (uid,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "coin": row[1], "lv": row[2], "inv": json.loads(row[3])}
    return {"id": uid, "coin": 1500, "lv": 1, "inv": {}}

def save_player(p):
    conn = sqlite3.connect('atlas_data.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)", 
              (p["id"], p["coin"], p["lv"], json.dumps(p["inv"])))
    conn.commit()
    conn.close()

init_db()

# --- لوحة تحكم السلطانة (ADMIN) ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💰 منحة ملكية (50k)", callback_data="adm_gift"))
        bot.send_message(message.chat.id, "🌟 **أهلاً سلطانة زينب**\nإليكِ صلاحيات التحكم الكامل بالبوت:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "adm_gift")
def adm_gift(call):
    p = get_player(call.from_user.id)
    p["coin"] += 50000
    save_player(p)
    bot.answer_callback_query(call.id, "تم تحديث الخزينة بنجاح! ✅")

# --- نظام السفر والأنيميشن ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("travel_"))
def handle_travel(call):
    dest = call.data.split("_")[1]
    # أنيميشن الرموز التعبيرية
    frames = ["🐫 جاري شد الرحال... \n`[ 🚢 ————— ]`", "🐫 جاري شد الرحال... \n`[ ——— 🚢 ——— ]`", "🐫 جاري شد الرحال... \n`[ ————— 🚢 ]`"]
    for frame in frames:
        try:
            bot.edit_message_caption(frame, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
            time.sleep(0.5)
        except: pass
    
    data = MARKET_DATA[dest]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"شراء {data['item']}", callback_data=f"buy_{dest}"))
    bot.send_photo(call.message.chat.id, data['img'], 
                   caption=f"📍 وصلنا إلى **{dest}**\n📦 السلعة: {data['item']}\n💰 السعر: {data['buy']} دج", 
                   parse_mode="Markdown", reply_markup=markup)

# --- البداية والقائمة الرئيسية ---
@bot.message_handler(commands=['start'])
def welcome(message):
    p = get_player(message.from_user.id)
    save_player(p)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🗺️ الخريطة", "🎒 حقيبتي", "🏰 القصر")
    bot.send_photo(message.chat.id, IMAGES["MAIN"], 
                   caption=f"🏰 **أهلاً بك في أطلس السلطانة**\nرصيدك الحالي: {p['coin']} دج\n\nابدأ تجارتك وابنِ مجدك!", 
                   reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🗺️ الخريطة")
def show_map(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(k, callback_data=f"travel_{k}") for k in MARKET_DATA.keys()]
    markup.add(*btns)
    bot.send_message(message.chat.id, "اختر وجهتك القادمة:", reply_markup=markup)

bot.infinity_polling()
