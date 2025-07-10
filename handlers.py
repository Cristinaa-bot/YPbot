from aiogram import Router, F, types
from aiogram.filters import Command
from config import ADMINS
from utils import save_profile, get_profiles_by_city
from keyboards import get_vote_keyboard

router = Router()

user_profiles = {}  # {user_id: {"step": ..., "text": ..., "photo": ...}}

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
        await msg.bot.send_photo(chat_id=msg.chat.id, photo=prof["photo"])
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
    user_profiles[msg.from_user.id]["step"] = "photo"
    await msg.answer("📸 Ora invia una foto.")

@router.message(F.photo)
async def get_photo(msg: types.Message):
    uid = msg.from_user.id
    if uid not in user_profiles or user_profiles[uid]["step"] != "photo":
        return
    photo_id = msg.photo[-1].file_id
    user_profiles[uid]["photo"] = photo_id
    await msg.answer("✅ Foto ricevuta. Ora invia /done per pubblicare.")

@router.message(Command("done"))
async def publish(msg: types.Message):
    uid = msg.from_user.id
    if uid not in user_profiles:
        await msg.answer("❗️Nessun profilo in corso.")
        return

    profile = user_profiles[uid]
    if "photo" not in profile:
        await msg.answer("❗️Manca la foto.")
        return

    text = profile["text"]
    photo = profile["photo"]
    city = text.split("\n")[2].strip()
    profile_id = save_profile(text, photo, city)

    await msg.bot.send_photo(chat_id=msg.chat.id, photo=photo)
    await msg.answer(text, reply_markup=get_vote_keyboard(profile_id))
    await msg.answer("✅ Profilo pubblicato.")

    del user_profiles[uid]
