from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import ADMINS, CITIES
from keyboards import city_keyboard
import json

router = Router()
profiles = {}
photos = {}

def register_handlers(dp, bot):
    dp.include_router(router)

@router.message(Command("start"))
async def start_cmd(msg: Message):
    await msg.answer("📍 Seleziona una città:", reply_markup=city_keyboard())

@router.message(Command("newprofile"))
async def new_profile(msg: Message):
    if msg.from_user.id not in ADMINS:
        return
    await msg.answer("Invia 8 righe:
Nome
Età
Città
Nazionalità
Date
Disponibilità
Preferenze
WhatsApp")
    profiles[msg.from_user.id] = {"step": "text"}

@router.message(F.text & F.from_user.id.in_(ADMINS))
async def handle_text(msg: Message):
    if msg.from_user.id in profiles and profiles[msg.from_user.id]["step"] == "text":
        lines = msg.text.strip().split("\n")
        if len(lines) != 8:
            return await msg.answer("Invia esattamente 8 righe.")
        keys = ["name", "age", "city", "nationality", "dates", "availability", "preferences", "whatsapp"]
        data = dict(zip(keys, lines))
        profiles[msg.from_user.id].update(data)
        profiles[msg.from_user.id]["step"] = "photos"
        await msg.answer("Ora invia 5 foto (tutte insieme).")

@router.message(F.media_group_id & F.photo)
async def handle_album(msg: Message):
    user_id = msg.from_user.id
    if user_id in profiles and profiles[user_id]["step"] == "photos":
        media_id = str(msg.media_group_id)
        if media_id not in photos:
            photos[media_id] = []
        photos[media_id].append(msg.photo[-1].file_id)

@router.message(Command("done"))
async def finalize(msg: Message):
    user_id = msg.from_user.id
    if user_id not in profiles or profiles[user_id]["step"] != "photos":
        return await msg.answer("Nessun profilo in corso.")
    # Найти фото по последнему альбому
    last_album = list(photos.values())[-1]
    if len(last_album) != 5:
        return await msg.answer("Devi inviare esattamente 5 foto.")
    data = profiles.pop(user_id)
    text = f"👤 <b>{data['name']}, {data['age']}</b>
"
    text += f"📍 {data['city']}
📅 {data['dates']}
✨ {data['preferences']}
"
    text += f"<b>WhatsApp:</b> <a href='https://wa.me/{data['whatsapp'].replace('+','')}'>Contatta</a>"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Pulizia", callback_data="rate:Pulizia"),
         InlineKeyboardButton(text="🍷 Servizio", callback_data="rate:Servizio"),
         InlineKeyboardButton(text="💅 Bellezza", callback_data="rate:Bellezza")]
    ])
    media = [InputMediaPhoto(media=ph) for ph in last_album]
    await msg.answer_media_group(media)
    await msg.answer(text, reply_markup=kb, disable_web_page_preview=True)
