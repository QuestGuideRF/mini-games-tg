from aiogram .types import ReplyKeyboardMarkup ,KeyboardButton
craps_game_actions =ReplyKeyboardMarkup (
resize_keyboard =True ,
keyboard =[
[KeyboardButton (text ="⛔️ Сдаться и остановить игру ⛔️")],
[KeyboardButton (text ="🔎 Правила игры 🔎")],
],
one_time_keyboard =True
)
gallows_game_actions =ReplyKeyboardMarkup (
resize_keyboard =True ,
keyboard =[
[KeyboardButton (text ="⛔️ Сдаться ⛔️")],
[KeyboardButton (text ="🔎 Правила 🔎")],
],
one_time_keyboard =True
)
blackjack_game_actions =ReplyKeyboardMarkup (
resize_keyboard =True ,
keyboard =[
[KeyboardButton (text ='⛔️ Сдаюсь ⛔️')],
[KeyboardButton (text ='🔎 Подсмотреть правила 🔎')],
],
one_time_keyboard =True
)
fool_game_actions =ReplyKeyboardMarkup (
resize_keyboard =True ,
keyboard =[
[KeyboardButton (text ='⛔️ Сдаться и остаться в дураках ⛔️')],
],
one_time_keyboard =True
)