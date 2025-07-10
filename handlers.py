from aiogram import Router, F, types
from aiogram.filters import Command
from config import ADMINS
from utils import save_profile, get_profiles_by_city
from keyboards import get_vote_keyboard

router = Router()

user_profiles = {}
media_groups = {}

@router.message(Command("start"))
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text="Milano")],
        [types.KeyboardButton(text="Roma")],
        [types.KeyboardButton(text="Firenze")]
    ])
    await msg.answer("Seleziona una città:", reply_markup=kb)

@router.message(F.text.in_(["Milano", "Roma", "Firenze"]))
async def city_selected(msg: types.Message):
    profiles = get_profiles_by_city(msg.text)
    if not profiles:
        await msg.answer("Nessun profilo disponibile in questa città. Nuovi arrivi in arrivo, resta sintonizzato!")
    else:
        for prof in profiles:
            media = [types.InputMediaPhoto(media=p) for p in prof["photos"]]
            await msg.bot.send_media_group(msg.chat.id, media)
            await msg.answer(prof["text"], reply_markup=get_vote_keyboard(prof["id"]))

@router.message(Command("newprofile"))
async def new_profile(msg: types.Message):
    if msg.from_user.id not in ADMINS:
        return
    await msg.answer("✍️ Invia 8 righe:")
    user_profiles[msg.from_user.id] = {"step": "text"}

@router.message(F.text, lambda msg: msg.from_user.id in user_profiles and user_profiles[msg.from_user.id]["step"] == "text")
async def profile_text(msg: types.Message):
    lines = msg.text.strip().split("\n")
    if len(lines) != 8:
        await msg.answer("❗️Invia esattamente 8 righe.")
        return
    user_profiles[msg.from_user.id]["text"] = msg.text
    user_profiles[msg.from_user.id]["step"] = "photos"
    await msg.answer("📸 Invia 5 foto insieme come album.")

@router.message(F.media_group_id, F.photo)
async def handle_album(msg: types.Message):
    uid = msg.from_user.id
    if uid not in user_profiles or user_profiles[uid]["step"] != "photos":
        return

    mgid = msg.media_group_id
    if mgid not in media_groups:
        media_groups[mgid] = []
    media_groups[mgid].append(msg.photo[-1].file_id)
    user_profiles[uid]["media_group_id"] = mgid

@router.message(Command("done"))
async def finish_profile(msg: types.Message):
    uid = msg.from_user.id
    if uid not in user_profiles:
        await msg.answer("❗️Nessun profilo in corso.")
        return

    text = user_profiles[uid]["text"]
    mgid = user_profiles[uid].get("media_group_id")
    photos = media_groups.get(mgid, [])

    if len(photos) != 5:
        await msg.answer("❗️Devi inviare esattamente 5 foto come album.")
        return

    city = text.strip().split("\n")[2]
    profile_id = save_profile(text, photos, city)

    media = [types.InputMediaPhoto(p) for p in photos]
    await msg.bot.send_media_group(msg.chat.id, media)
    await msg.answer(text, reply_markup=get_vote_keyboard(profile_id))
    await msg.answer("✅ Profilo pubblicato.")

    del user_profiles[uid]
    del media_groups[mgid]
