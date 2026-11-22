from aiogram .types import InlineKeyboardMarkup ,InlineKeyboardButton
async def blackjack_start_game ()->InlineKeyboardMarkup :
    keyboard =InlineKeyboardMarkup ()
    keyboard .add (InlineKeyboardButton (text ='♣️ Играем ♠️',callback_data ='blackjack_start_game'))
    return keyboard
async def blackjack_next_round ()->InlineKeyboardMarkup :
    keyboard =InlineKeyboardMarkup ()
    keyboard .add (InlineKeyboardButton (text ='♣️ Далее ... ♠️',callback_data ='blackjack_next_round'))
    return keyboard
async def take_card ()->InlineKeyboardMarkup :
    keyboard =InlineKeyboardMarkup ()
    keyboard .add (InlineKeyboardButton (text ='Взять карту',callback_data ='take_card'))
    return keyboard
async def bot_takes_card ()->InlineKeyboardMarkup :
    keyboard =InlineKeyboardMarkup ()
    keyboard .add (InlineKeyboardButton (text ='Ок',callback_data ='bot_takes_card'))
    return keyboard
async def blackjack_action_choice ()->InlineKeyboardMarkup :
    keyboard =InlineKeyboardMarkup ()
    keyboard .add (InlineKeyboardButton (text ='Ещё...',callback_data ='take_card'))
    keyboard .add (InlineKeyboardButton (text ='Хватит',callback_data ='enough_card'))
    return keyboard