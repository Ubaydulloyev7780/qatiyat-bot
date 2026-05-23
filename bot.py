#!/usr/bin/env python3
import os
import json
import asyncio
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, JobQueue
)

TOKEN = os.environ.get("BOT_TOKEN", "8912448991:AAGTLDeCWVMoEhCiO4DTFwbzmF989BDxETo")
DATA_FILE = "user_data.json"

TASKS = [
    {"id": "namoz", "emoji": "🕌", "text": "Bomdod namozi o'qidim"},
    {"id": "sport", "emoji": "🏃", "text": "Sport / yurish (20 daqiqa)"},
    {"id": "ish",   "emoji": "🔨", "text": "Malyar ishi bajardim"},
    {"id": "data",  "emoji": "💻", "text": "Data Science o'qidim"},
    {"id": "qarz",  "emoji": "💰", "text": "Qarz uchun pul ajratdim"},
    {"id": "kech",  "emoji": "📓", "text": "Kechki 3 savol yozdim"},
]

GOALS = [
    "💳 6 mln so'm qarz to'lash",
    "📈 Trading uchun 100k prop shot (600$)",
    "🏠 Oila uchun 3 mln so'm",
    "📊 Data Science kursini tugatish",
    "🕌 Namozni odatga aylantirish",
    "🏃 Sportni odatga aylantirish",
]

MORNING_MOTIVATIONS = [
    "Bismillah! Bugun yana bir kun — yana bir imkoniyat. Qarz kamayadi, kuch ortadi! 💪",
    "Har kuni 1% yaxshilanish — 40 kunda o'zingni tanimay qolasan. Boshla! 🚀",
    "Namoz — kuchning manbai. Sport — tanning quvvati. Ish — ertangning poydevori. Davom et! 🌅",
    "Bugun malyar ishiga boring, har bir so'm qarzingni kamaytiradi. Oldinga! 💰",
    "Prop shot orzuing bor — bugun o'sha orzuga bir qadam yaqinlash! 📈",
    "Oilang sening kuchingni kutmoqda. Bugun ularuchun ishlaysiz! ❤️",
    "Bir kun o'tdi — buni o'zgartira olmaysan. Bugunni — o'zgartirishingiz mumkin! ⚡",
]

EVENING_MOTIVATIONS = [
    "Bugun qanday kechdi? Hech bo'lmasa bitta yaxshi ish qildingmi? O'sha kifoya! ✅",
    "Kecha o'tdi. Ertaga yangi imkoniyat. Uxlashdan oldin namoz o'qi va shukr qil! 🌙",
    "Har kecha o'zingga so'ra: bugun qarzimga nima qildim? Javob yaxshi bo'lsin! 💪",
    "Data Science o'qiding? Namoz o'qiding? Sport qilding? Bittasi bo'lsa ham — davom et! 🎯",
    "40 kun — bu bir umr emas. Lekin bu 40 kun umringni o'zgartiradi! 🔥",
    "Charchagan bo'lsang ham — ertaga bomdodga tur. O'sha bitta qadam hamma narsani boshlaydi! 🌟",
]

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "start_date": date.today().isoformat(),
            "days": {},
            "chat_id": None
        }
    return data[uid]

def get_day_num(user):
    start = date.fromisoformat(user["start_date"])
    diff = (date.today() - start).days + 1
    return min(max(diff, 1), 40)

def today_key():
    return date.today().isoformat()

def get_streak(user):
    streak = 0
    check = date.today()
    while True:
        key = check.isoformat()
        d = user["days"].get(key, {})
        done = sum(1 for t in TASKS if d.get(t["id"]))
        if done >= len(TASKS):
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = get_user(data, update.effective_user.id)
    user["chat_id"] = update.effective_chat.id
    save_data(data)

    await update.message.reply_text(
        "🌟 *Assalomu alaykum! Qat'iyat Botiga xush kelibsiz!*\n\n"
        "Bu bot sizning 40 kunlik o'zgarish yo'lingizda yordamchi bo'ladi.\n\n"
        "📋 *Maqsadlaringiz:*\n" + "\n".join(GOALS) + "\n\n"
        "Har kuni vazifalarni belgilang, motivatsiya oling, progressing kuzating!\n\n"
        "👇 Menyuni ko'rish uchun /menu bosing",
        parse_mode="Markdown"
    )

async def menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Bugungi vazifalar", callback_data="tasks")],
        [InlineKeyboardButton("📊 Mening progressim", callback_data="progress")],
        [InlineKeyboardButton("🎯 Maqsadlarim", callback_data="goals")],
        [InlineKeyboardButton("💪 Motivatsiya ber", callback_data="motivate")],
        [InlineKeyboardButton("📅 40 kunlik yo'l", callback_data="journey")],
    ]
    await update.message.reply_text(
        "📱 *Asosiy menyu:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)
    user["chat_id"] = query.message.chat_id
    action = query.data

    if action == "tasks":
        await show_tasks(query, user, data)
    elif action.startswith("toggle_"):
        task_id = action.replace("toggle_", "")
        key = today_key()
        if key not in user["days"]:
            user["days"][key] = {}
        user["days"][key][task_id] = not user["days"][key].get(task_id, False)
        save_data(data)
        await show_tasks(query, user, data)
    elif action == "progress":
        await show_progress(query, user)
    elif action == "goals":
        await show_goals(query)
    elif action == "motivate":
        await show_motivation(query)
    elif action == "journey":
        await show_journey(query, user)
    elif action == "menu":
        keyboard = [
            [InlineKeyboardButton("✅ Bugungi vazifalar", callback_data="tasks")],
            [InlineKeyboardButton("📊 Mening progressim", callback_data="progress")],
            [InlineKeyboardButton("🎯 Maqsadlarim", callback_data="goals")],
            [InlineKeyboardButton("💪 Motivatsiya ber", callback_data="motivate")],
            [InlineKeyboardButton("📅 40 kunlik yo'l", callback_data="journey")],
        ]
        await query.edit_message_text(
            "📱 *Asosiy menyu:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_tasks(query, user, data):
    day_num = get_day_num(user)
    key = today_key()
    today = user["days"].get(key, {})
    done_count = sum(1 for t in TASKS if today.get(t["id"]))

    text = f"✅ *{day_num}-kun — Bugungi vazifalar:*\n\n"
    keyboard = []
    for t in TASKS:
        done = today.get(t["id"], False)
        check = "✅" if done else "⬜"
        keyboard.append([InlineKeyboardButton(
            f"{check} {t['emoji']} {t['text']}",
            callback_data=f"toggle_{t['id']}"
        )])
    
    text += f"Bajarildi: *{done_count}/{len(TASKS)}*\n"
    if done_count == len(TASKS):
        text += "\n🎉 Zo'r! Bugun barchasi bajarildi!"
    
    keyboard.append([InlineKeyboardButton("🔙 Menyu", callback_data="menu")])
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    save_data(data)

async def show_progress(query, user):
    day_num = get_day_num(user)
    streak = get_streak(user)
    
    total_done = 0
    full_days = 0
    for key, day_data in user["days"].items():
        cnt = sum(1 for t in TASKS if day_data.get(t["id"]))
        total_done += cnt
        if cnt >= len(TASKS):
            full_days += 1

    pct = round((day_num - 1) / 40 * 100)
    bar_filled = int(pct / 10)
    bar = "🟩" * bar_filled + "⬜" * (10 - bar_filled)

    text = (
        f"📊 *Sizning progressingiz:*\n\n"
        f"📅 Kun: *{day_num}/40*\n"
        f"🔥 Ketma-ket: *{streak} kun*\n"
        f"⭐ To'liq kunlar: *{full_days}*\n"
        f"✅ Jami vazifa: *{total_done}*\n\n"
        f"*40 kunlik yo'l:*\n{bar} {pct}%\n\n"
    )
    
    if day_num <= 10:
        text += "💪 Boshlanish — eng qiyin qadamdir. Davom et!"
    elif day_num <= 20:
        text += "🚀 Yarim yo'lga yaqinlashmoqda! Zo'r ketmoqda!"
    elif day_num <= 35:
        text += "🔥 Finish chizig'i ko'rinmoqda! To'xtama!"
    else:
        text += "🏆 Oxirgi kunlar! Sen g'olibsan!"

    keyboard = [[InlineKeyboardButton("🔙 Menyu", callback_data="menu")]]
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_goals(query):
    text = "🎯 *40 kunlik maqsadlaringiz:*\n\n"
    text += "\n".join(GOALS)
    text += "\n\n💡 Har kuni shu maqsadlarni eslab turing!"
    keyboard = [[InlineKeyboardButton("🔙 Menyu", callback_data="menu")]]
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_motivation(query):
    import random
    all_quotes = MORNING_MOTIVATIONS + EVENING_MOTIVATIONS
    quote = random.choice(all_quotes)
    text = f"💪 *Motivatsiya:*\n\n{quote}"
    keyboard = [
        [InlineKeyboardButton("🔄 Yana bittasi", callback_data="motivate")],
        [InlineKeyboardButton("🔙 Menyu", callback_data="menu")],
    ]
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_journey(query, user):
    day_num = get_day_num(user)
    text = "📅 *40 kunlik yo'l:*\n\n"
    line = ""
    for i in range(1, 41):
        key_d = (date.fromisoformat(user["start_date"]) + timedelta(days=i-1)).isoformat()
        d = user["days"].get(key_d, {})
        cnt = sum(1 for t in TASKS if d.get(t["id"]))
        if i < day_num:
            if cnt >= len(TASKS):
                line += "🟩"
            elif cnt > 0:
                line += "🟨"
            else:
                line += "🟥"
        elif i == day_num:
            line += "⭐"
        else:
            line += "⬜"
        if i % 10 == 0:
            text += line + f" ({i})\n"
            line = ""
    
    text += "\n🟩 To'liq  🟨 Qisman  🟥 O'tkazib  ⭐ Bugun  ⬜ Kelasi"
    keyboard = [[InlineKeyboardButton("🔙 Menyu", callback_data="menu")]]
    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_morning_motivation(ctx: ContextTypes.DEFAULT_TYPE):
    import random
    data = load_data()
    quote = random.choice(MORNING_MOTIVATIONS)
    for uid, user in data.items():
        chat_id = user.get("chat_id")
        if not chat_id:
            continue
        day_num = get_day_num(user)
        keyboard = [[InlineKeyboardButton("✅ Vazifalarni ko'rish", callback_data="tasks")]]
        try:
            await ctx.bot.send_message(
                chat_id=chat_id,
                text=f"🌅 *Xayrli tong! {day_num}-kun boshlandi!*\n\n{quote}\n\n👇 Bugungi vazifalaringiz:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass

async def send_evening_motivation(ctx: ContextTypes.DEFAULT_TYPE):
    import random
    data = load_data()
    quote = random.choice(EVENING_MOTIVATIONS)
    for uid, user in data.items():
        chat_id = user.get("chat_id")
        if not chat_id:
            continue
        key = today_key()
        today = user["days"].get(key, {})
        done_count = sum(1 for t in TASKS if today.get(t["id"]))
        keyboard = [[InlineKeyboardButton("📊 Progressimni ko'rish", callback_data="progress")]]
        try:
            await ctx.bot.send_message(
                chat_id=chat_id,
                text=f"🌙 *Kechqurun salom!*\n\n{quote}\n\n✅ Bugun: *{done_count}/{len(TASKS)}* vazifa bajarildi.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Ertalab soat 6:00 (UTC+5 = 1:00 UTC)
    app.job_queue.run_daily(
        send_morning_motivation,
        time=datetime.strptime("01:00", "%H:%M").time()
    )
    # Kechqurun soat 21:00 (UTC+5 = 16:00 UTC)
    app.job_queue.run_daily(
        send_evening_motivation,
        time=datetime.strptime("16:00", "%H:%M").time()
    )

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
