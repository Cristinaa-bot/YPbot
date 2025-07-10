from aiogram import Router, F, types
from aiogram.filters import Command
from config import ADMINS
from utils import save_profile, get_profiles_by_city
from keyboards import get_vote_keyboard

router = Router()

user_profiles = {}     # {user_id: {"step": ..., "text": ..., "media_group_id": ...}}
media_groups = {}      # {media_group_id: [file_id, ...]}

@router.message(Command("start"))
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text="Milano")],
        [types.KeyboardButton(text="Roma")],
        [types.KeyboardButton(text="Firenze")]
    ])
    await msg.answer("Seleziona una città:", reply_markup=kb)

@router.message(F.text.in_(["Milano", "Roma", "Firenze"]))
async def show_profiles(msg: types.Message):
    city = msg.text
    profiles = get_profiles_by_city(city)
    if not profiles:
        await msg.answer("Nessun profilo disponibile in questa città. Nuovi arrivi in arrivo, resta sintonizzato!")
        return

    for prof in profiles:
        media = [types.InputMediaPhoto(media=photo) for photo in prof['photos']]
        await msg.bot.send_media_group(msg.chat.id, media)
        await msg.answer(prof["text"], reply_markup=get_vote_keyboard(prof["id"]))

@router.message(Command("newprofile"))
async def newprofile(msg: types.Message):
    if msg.from_user.id not in ADMINS:
        return
    await msg.answer("✍️ Invia 8 righe di testo.")
    user_profiles[msg.from_user.id] = {"step": "text"}

@router.message(lambda msg: msg.from_user.id in user_profiles and user_profiles[msg.from_user.id]["step"] == "text")
async def get_text(msg: types.Message):
    lines = msg.text.strip().split("\n")
    if len(lines) != 8:
        await msg.answer("❗️Invia esattamente 8 righe.")
        return
    user_profiles[msg.from_user.id]["text"] = msg.text
    user_profiles[msg.from_user.id]["step"] = "photos"
    await msg.answer("📸 Ora invia 5 foto come album.")

@router.message(F.media_group_id, F.photo)
async def album_photo(msg: types.Message):
    user_id = msg.from_user.id
    if user_id not in user_profiles or user_profiles[user_id]["step"] != "photos":
        return

    mgid = msg.media_group_id
    if mgid not in media_groups:
        media_groups[mgid] = []
    media_groups[mgid].append(msg.photo[-1].file_id)

    user_profiles[user_id]["media_group_id"] = mgid

@router.message(Command("done"))
async def finish(msg: types.Message):
    uid = msg.from_user.id
    if uid not in user_profiles:
        await msg.answer("❗️Nessun profilo in corso.")
        return

    profile = user_profiles[uid]
    mgid = profile.get("media_group_id")
    photos = media_groups.get(mgid, [])

    if not photos or len(photos) != 5:
        await msg.answer("❗️Invia esattamente 5 foto come album prima di /done.")
        return

    profile_text = profile["text"]
    city = profile_text.split("\n")[2].strip()
    profile_id = save_profile(profile_text, photos, city)

    media = [types.InputMediaPhoto(photo) for photo in photos]
    await msg.bot.send_media_group(chat_id=msg.chat.id, media=media)
    await msg.answer(profile_text, reply_markup=get_vote_keyboard(profile_id))
    await msg.answer("✅ Profilo pubblicato.")

    # Очистка
    del user_profiles[uid]
    del media_groups[mgid]
