from aiogram import types
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import ADMINS, CITIES, CHANNEL_LINK
from keyboards import city_keyboard
import json, os
import sqlite3

router = Router()
user_states = {}
user_photos = {}

def register_handlers(dp, bot):
    dp.include_router(router)

# Команда /start
@router.message(Command("start"))
async def start_cmd(msg: Message):
    await msg.answer("📍 Seleziona una città:", reply_markup=city_keyboard())

# Выбор города
@router.callback_query(F.data.startswith("city:"))
async def city_selected(callback: CallbackQuery):
    city = callback.data.split(":")[1]
    conn = sqlite3.connect("data/bot.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM profiles WHERE city=? AND active=1 ORDER BY created_at DESC", (city,))
    profiles = cur.fetchall()
    conn.close()

    if not profiles:
        await callback.message.answer("❌ Nessun profilo disponibile in questa città. Nuovi arrivi in arrivo, resta sintonizzato!")
        return

    for profile in profiles:
        name, age, _, city, _, _, preferences, whatsapp, photos, *_ = profile[1:]
        text = f"👤 <b>{name}, {age}</b>\n📍 {city}\n✨ {preferences}\n"
        text += f"<b>WhatsApp:</b> <a href='https://wa.me/{whatsapp.replace('+','')}'>Contatta</a>"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌟 Pulizia", callback_data=f"rate:{profile[0]}:Pulizia"),
             InlineKeyboardButton(text="🍷 Servizio", callback_data=f"rate:{profile[0]}:Servizio"),
             InlineKeyboardButton(text="💅 Bellezza", callback_data=f"rate:{profile[0]}:Bellezza")]
        ])
        media = [InputMediaPhoto(media=ph) for ph in profile[8].split(";")]
        await callback.message.answer_media_group(media)
        await callback.message.answer(text, reply_markup=kb, disable_web_page_preview=True)

# Команда /newprofile (только для админа)
@router.message(Command("newprofile"))
async def new_profile(msg: Message):
    if msg.from_user.id not in ADMINS:
        return
    await msg.answer("Invia 8 righe:\nNome\nEtà\nCittà\nNazionalità\nDate\nDisponibilità\nPreferenze\nWhatsApp")
    user_states[msg.from_user.id] = {"step": "text"}

# Обработка текста анкеты
@router.message(F.text)
async def handle_text(msg: Message):
    if msg.from_user.id in user_states and user_states[msg.from_user.id]["step"] == "text":
        lines = msg.text.strip().split("\n")
        if len(lines) != 8:
            return await msg.answer("⚠️ Invia esattamente 8 righe.")
        keys = ["name", "age", "city", "nationality", "dates", "availability", "preferences", "whatsapp"]
        data = dict(zip(keys, lines))
        user_states[msg.from_user.id].update(data)
        user_states[msg.from_user.id]["step"] = "photos"
        await msg.answer("✅ Ora invia 5 foto tutte insieme (album).")

# Приём фото
@router.message(F.media_group_id & F.photo)
async def handle_album(msg: Message):
    uid = msg.from_user.id
    media_id = msg.media_group_id
    if uid in user_states and user_states[uid]["step"] == "photos":
        if uid not in user_photos:
            user_photos[uid] = []
        user_photos[uid].append(msg.photo[-1].file_id)

# Команда /done завершает анкету
@router.message(Command("done"))
async def finish_profile(msg: types.Message):
    if msg.from_user.id not in user_profiles:
        await msg.answer("❗️Nessun profilo in corso.")
        return

    media_group_id = user_profiles[msg.from_user.id].get("media_group_id")
    photos = user_photos.get(media_group_id, [])

    if not media_group_id or len(photos) != 5:
        await msg.answer("❗️Invia esattamente 5 foto come album prima di completare.")
        return

    profile_text = user_profiles[msg.from_user.id]["text"]
    lines = profile_text.strip().split("\n")
    city = lines[2].strip()

    profile_id = save_profile(profile_text, photos, city)

    media = [types.InputMediaPhoto(media=p) for p in photos]
    await msg.bot.send_media_group(msg.chat.id, media)
    await msg.answer(profile_text, reply_markup=get_vote_keyboard(profile_id))
    await msg.answer("✅ Profilo pubblicato.")

    # Очистка
    del user_profiles[msg.from_user.id]
    del user_photos[media_group_id]

    # Сохраняем в базу
    conn = sqlite3.connect("data/bot.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO profiles (name, age, city, nationality, dates, availability, preferences, whatsapp, photos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (data["name"], data["age"], data["city"], data["nationality"], data["dates"], data["availability"], data["preferences"], data["whatsapp"], photos_str))
    conn.commit()
    profile_id = cur.lastrowid
    conn.close()

    # Публикуем
    text = f"👤 <b>{data['name']}, {data['age']}</b>\n📍 {data['city']}\n📅 {data['dates']}\n✨ {data['preferences']}\n"
    text += f"<b>WhatsApp:</b> <a href='https://wa.me/{data['whatsapp'].replace('+','')}'>Contatta</a>"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Pulizia", callback_data=f"rate:{profile_id}:Pulizia"),
         InlineKeyboardButton(text="🍷 Servizio", callback_data=f"rate:{profile_id}:Servizio"),
         InlineKeyboardButton(text="💅 Bellezza", callback_data=f"rate:{profile_id}:Bellezza")]
    ])
    media = [InputMediaPhoto(media=ph) for ph in photos]
    await msg.answer_media_group(media)
    await msg.answer(text, reply_markup=kb, disable_web_page_preview=True)
