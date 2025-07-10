from aiogram import types

def get_vote_keyboard(profile_id):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🌟 Pulizia", callback_data=f"vote:clean:{profile_id}"),
            types.InlineKeyboardButton(text="🍷 Servizio", callback_data=f"vote:service:{profile_id}"),
            types.InlineKeyboardButton(text="💅 Bellezza", callback_data=f"vote:beauty:{profile_id}")
        ]
    ])
    return kb
