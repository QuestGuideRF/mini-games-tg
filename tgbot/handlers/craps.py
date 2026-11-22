from asyncio import sleep
from aiogram import Dispatcher
from aiogram .dispatcher import FSMContext
from aiogram .dispatcher .filters import Text
from aiogram .types import Message ,CallbackQuery ,ReplyKeyboardRemove
from tgbot .keyboards .inline_craps import bot_roll ,do_roll ,bot_reroll ,craps_start_game
from tgbot .keyboards .reply import craps_game_actions
from tgbot .misc .factories import for_reroll ,for_reroll_done
from tgbot .services .craps_service import play_round ,finish_game ,save_result ,play_reroll ,play_turn ,set_winner ,ask_reroll ,choose_dices_for_bots_reroll ,should_bot_reroll
from tgbot .services .default_commands import get_default_commands
from tgbot .services .printer import print_craps_rules ,print_emotion
async def craps (message :Message ,state :FSMContext ):
    await state .finish ()
    await print_craps_rules (message )
    await message .answer ('Сыграем?',reply_markup =await craps_start_game ())
async def give_up (message :Message ,state :FSMContext ):
    await state .finish ()
    await print_emotion (message =message ,bot_win =True )
    await sleep (3 )
    commands =await get_default_commands ()
    await message .answer (f"🤖 Во что сыграем?\n\n{commands }",reply_markup =ReplyKeyboardRemove ())
async def show_rules (message :Message ):
    await print_craps_rules (message )
async def start_craps (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    async with state .proxy ()as data :
        data ['round_counter']=1
        data ['player_score']=0
        data ['bot_score']=0
    await call .message .answer ('🤖 Начинаем новую игру.\nИграем до 5 очков.\nПоехали!!!',
    reply_markup =craps_game_actions )
    await sleep (3 )
    await play_round (call .message ,state )
    await call .message .delete ()
async def players_roll (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    player_mark ,player_summa ,player_result ,player_dice_list =await play_turn (call .message )
    await save_result (player_mark ,player_summa ,player_dice_list ,save_for ='player',state =state )
    await call .message .answer (f"🤵 Твой результат: <b>{player_result } ({player_summa })</b>",parse_mode ='html')
    await sleep (2 )
    states =await state .get_data ()
    last_winner =states .get ('last_winner')
    if last_winner is None or last_winner =='player':
        await call .message .answer (f'🤖 Мой бросок...',reply_markup =await bot_roll ())
    else :
        await call .message .answer (f'🤖 Теперь мой черёд...',reply_markup =await bot_reroll ())
async def bots_roll (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    bot_mark ,bot_summa ,bot_result ,bot_dice_list =await play_turn (call .message )
    await save_result (bot_mark ,bot_summa ,bot_dice_list ,save_for ='bot',state =state )
    await call .message .answer (f"🤖 Мой результат: <b>{bot_result } ({bot_summa })</b>",parse_mode ='html')
    await sleep (2 )
    states =await state .get_data ()
    last_winner =states .get ('last_winner')
    if last_winner =='bot':
        await call .message .answer (f'🤵 Твой бросок...',reply_markup =await do_roll ())
    else :
        await ask_reroll (call .message ,state )
async def bots_reroll (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    is_reroll =await should_bot_reroll (call .message ,state )
    if is_reroll :
        await call .message .answer (f"🤖 Я перебрасываю...")
        dices_for_bots_reroll =await choose_dices_for_bots_reroll (call .message ,state )
        if dices_for_bots_reroll =='all':
            bot_mark ,bot_summa ,bot_result ,bot_dice_list =await play_turn (call .message )
        else :
            bot_mark ,bot_summa ,bot_result ,bot_dice_list =await play_reroll (call .message ,state ,'bot')
        await save_result (bot_mark ,bot_summa ,bot_dice_list ,save_for ='bot',state =state )
        await call .message .answer (f"🤖 Мой результат: <b>{bot_result } ({bot_summa })</b>",parse_mode ='html')
    states =await state .get_data ()
    if states .get ('last_winner')=='bot':
        await ask_reroll (call .message ,state )
    else :
        await set_winner (call .message ,state )
async def get_dice_for_reroll (call :CallbackQuery ,callback_data :dict ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    dice_value =callback_data .get ('dice_value')
    states =await state .get_data ()
    player_dice_list =states .get ('player_dice_list')
    player_dice_list .remove (int (dice_value ))
    async with state .proxy ()as data :
        data ['player_dice_list']=player_dice_list
    await ask_reroll (call .message ,state )
    await call .message .delete ()
async def reroll_done (call :CallbackQuery ,callback_data :dict ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    states =await state .get_data ()
    if callback_data .get ('action')=='reroll_done':
        player_mark ,player_summa ,player_result ,player_dice_list =await play_reroll (call .message ,state ,'player')
    else :
        player_mark ,player_summa ,player_result ,player_dice_list =await play_turn (call .message )
    await save_result (player_mark ,player_summa ,player_dice_list ,save_for ='player',state =state )
    await call .message .answer (f"🤵 Твой результат: <b>{player_result } ({player_summa })</b>",parse_mode ='html')
    await sleep (2 )
    if states .get ('last_winner')=='bot':
        await set_winner (call .message ,state )
    else :
        await call .message .answer (f'🤖 Теперь мой черёд...',reply_markup =await bot_reroll ())
async def next_round (call :CallbackQuery ,state :FSMContext ):
    await call .message .edit_reply_markup (reply_markup =None )
    states =await state .get_data ()
    player_score =states .get ('player_score')
    bot_score =states .get ('bot_score')
    if player_score ==5 or bot_score ==5 :
        await finish_game (call .message ,player_score ,bot_score ,state )
    else :
        round =states .get ('round_counter')
        round +=1
        async with state .proxy ()as data :
            data ['round_counter']=round
        await play_round (call .message ,state )
def register_craps (dp :Dispatcher ):
    dp .register_message_handler (craps ,commands =["craps"],state ="*")
    dp .register_message_handler (give_up ,Text (equals ='⛔️ Сдаться и остановить игру ⛔️'))
    dp .register_message_handler (show_rules ,Text (equals ='🔎 Правила игры 🔎'))
    dp .register_callback_query_handler (start_craps ,text ='craps_start_game',state ="*")
    dp .register_callback_query_handler (players_roll ,text ='do_roll',state ="*")
    dp .register_callback_query_handler (reroll_done ,for_reroll_done .filter (),state ="*")
    dp .register_callback_query_handler (next_round ,text ='next_round',state ="*")
    dp .register_callback_query_handler (bots_roll ,text ='bot_roll',state ="*")
    dp .register_callback_query_handler (bots_reroll ,text ='bot_reroll',state ="*")
    dp .register_callback_query_handler (get_dice_for_reroll ,for_reroll .filter (),state ="*"),