from asyncio import sleep
from aiogram import Dispatcher
from aiogram .dispatcher import FSMContext
from aiogram .dispatcher .filters import Text
from aiogram .types import Message ,CallbackQuery
from tgbot .keyboards .inline_blackjack import blackjack_start_game ,blackjack_action_choice ,take_card ,bot_takes_card ,blackjack_next_round
from tgbot .keyboards .reply import blackjack_game_actions
from tgbot .services .blackjack_service import play_blackjack_round ,play_blackjack_turn ,play_blackjack_bot_turn ,set_blackjack_winner ,finish_blackjack ,inc_round_counter ,check_fairplay
from tgbot .services .craps_service import reward_bot
from tgbot .services .printer import print_blackjack_rules ,print_cards
async def blackjack (message :Message ,state :FSMContext ):
    await state .finish ()
    await print_blackjack_rules (message )
    await message .answer ('Ну что, сразимся?',reply_markup =await blackjack_start_game ())
async def start_blackjack (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    async with state .proxy ()as data :
        data ['round_counter']=1
        data ['player_score']=0
        data ['bot_score']=0
    await call .message .answer (f"👍 Начинаем новую игру.\nИграем до 5 очков. Поехали!",
    reply_markup =blackjack_game_actions )
    await sleep (3 )
    await play_blackjack_round (call .message ,state )
    await call .message .delete ()
async def player_takes_card (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    await play_blackjack_turn (call .message ,state )
    if await check_fairplay (state ):
        await call .message .answer (f"Берёшь еще?",reply_markup =await blackjack_action_choice ())
    else :
        await inc_round_counter (state )
        await reward_bot (state )
        await call .message .answer ('🤖 Тебе засчитано поражение за попытку жульничества',
        reply_markup =await blackjack_next_round ())
    await call .message .delete ()
async def player_enough_card (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    states =await state .get_data ()
    last_winner =states .get ('last_winner')
    if last_winner is None or last_winner =='player':
        await call .message .answer (f'🤖 Мой ход...',reply_markup =await bot_takes_card ())
    else :
        await set_blackjack_winner (call .message ,state )
    await call .message .delete ()
async def bot_take_card (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    await play_blackjack_bot_turn (call .message ,state )
    states =await state .get_data ()
    cards =states .get ('bot_cards')
    await print_cards (call .message ,cards ,print_as ='close')
    last_winner =states .get ('last_winner')
    if last_winner is None or last_winner =='player':
        await set_blackjack_winner (call .message ,state )
    else :
        await call .message .answer (f'🤵 Твой ход...',reply_markup =await take_card ())
async def blackjack_next_round_handler (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    states =await state .get_data ()
    player_score ,bot_score =states .get ('player_score'),states .get ('bot_score')
    if player_score ==5 or bot_score ==5 :
        if player_score >bot_score :
            await call .message .answer (f'🔔 КОНЕЦ ИГРЫ! Счет:\n'
            f'Ты <b>{player_score }:{bot_score }</b> Я\n'
            f'🤵 Ты победил! 🎉🎉🎉',
            parse_mode ='html')
            await finish_blackjack (call .message ,state ,'player')
        else :
            await call .message .answer (f'🔔 КОНЕЦ ИГРЫ! Счет:\n'
            f'Ты <b>{player_score }:{bot_score }</b> Я\n'
            f'👤 Бот победил!',
            parse_mode ='html')
            await finish_blackjack (call .message ,state ,'bot')
    else :
        await play_blackjack_round (call .message ,state )
async def give_up_blackjack (message :Message ,state :FSMContext ):
    await finish_blackjack (message ,state ,'bot')
async def show_rules_blackjack (message :Message ):
    await print_blackjack_rules (message )
def register_blackjack (dp :Dispatcher ):
    dp .register_message_handler (blackjack ,commands =["blackjack"],state ="*")
    dp .register_callback_query_handler (start_blackjack ,text ='blackjack_start_game',state ="*")
    dp .register_message_handler (give_up_blackjack ,Text (equals ='⛔️ Сдаюсь ⛔️'),state ="*")
    dp .register_message_handler (show_rules_blackjack ,Text (equals ='🔎 Подсмотреть правила 🔎'),state ="*")
    dp .register_callback_query_handler (player_takes_card ,text ='take_card',state ="*")
    dp .register_callback_query_handler (blackjack_next_round_handler ,text ='blackjack_next_round',state ="*")
    dp .register_callback_query_handler (player_enough_card ,text ='enough_card',state ="*")
    dp .register_callback_query_handler (bot_take_card ,text ='bot_takes_card',state ="*")