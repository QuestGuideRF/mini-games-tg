from asyncio import sleep
from random import choice
from typing import Union
from aiogram .dispatcher import FSMContext
from aiogram .types import Message ,ReplyKeyboardRemove
from tgbot .keyboards .inline_fool import fool_player_turn ,propose_more_cards ,show_done_button ,player_cover ,show_next_button
from tgbot .services .default_commands import get_default_commands
from tgbot .services .printer import RUS_CARDS_VALUES ,print_fool_desk ,print_emotion
async def create_deck ()->list [str ]:
    return list (RUS_CARDS_VALUES .keys ())
async def check_who_first (trump :str ,player_cards :list [str ],bot_cards :list [str ])->str :
    players_trumps =[player_card for player_card in player_cards if player_card [-2 ]==trump [-2 ]]
    bots_trumps =[bot_card for bot_card in bot_cards if bot_card [-2 ]==trump [-2 ]]
    if players_trumps and bots_trumps :
        players_trumps_values =[RUS_CARDS_VALUES [card ]for card in players_trumps ]
        bots_trumps_values =[RUS_CARDS_VALUES [card ]for card in bots_trumps ]
        if min (bots_trumps_values )<min (players_trumps_values ):
            return 'bot'
        else :
            return 'player'
    elif players_trumps and not bots_trumps :
        return 'player'
    elif bots_trumps and not players_trumps :
        return 'bot'
    else :
        return choice (['player','bot'])
async def pick_card (state :FSMContext )->Union [str ,None ]:
    states =await state .get_data ()
    cards =states .get ('deck')
    trump =states .get ('trump')
    trump_used =states .get ('trump_used')
    if trump and len (cards )==0 and not trump_used :
        async with state .proxy ()as data :
            data ['trump_used']=True
        return trump
    try :
        card =choice (cards )
        cards .remove (card )
        async with state .proxy ()as data :
            data ['deck']=cards
        return card
    except IndexError :
        return None
async def hand_out_cards (state :FSMContext ,num :int )->list [str ]:
    cards =[await pick_card (state )for _ in range (num )]
    return [card for card in cards if card is not None ]
async def place_card_on_desk (state :FSMContext ,card :str ,place_for :str )->None :
    states =await state .get_data ()
    desk =states .get ('desk')
    desk .append (card )
    if place_for =='player':
        cards =states .get ('player_cards')
    else :
        cards =states .get ('bot_cards')
    cards .remove (card )
    async with state .proxy ()as data :
        if place_for =='player':
            data ['player_cards']=cards
        else :
            data ['bot_cards']=cards
        data ['desk']=desk
async def bot_choose_card_for_cover (state :FSMContext ,card :str )->Union [str ,None ]:
    states =await state .get_data ()
    bot_cards =states .get ('bot_cards')
    trump =states .get ('trump')
    deck =states .get ('deck')
    player_value =RUS_CARDS_VALUES [card ]
    player_suit =card [-2 ]
    if player_suit ==trump [-2 ]and player_value in [11 ,12 ,13 ,14 ]and len (deck )>6 :
        return None
    cards_for_cover =[
    bot_card for bot_card in bot_cards
    if (bot_card [-2 ]==player_suit and RUS_CARDS_VALUES [bot_card ]>player_value )
    ]
    if cards_for_cover :
        cards_for_cover_values =[RUS_CARDS_VALUES [bot_card ]for bot_card in cards_for_cover ]
        card_for_cover =[bot_card for bot_card in cards_for_cover
        if RUS_CARDS_VALUES [bot_card ]==min (cards_for_cover_values )]
        if player_suit ==trump [-2 ]and RUS_CARDS_VALUES [card_for_cover [0 ]]in [12 ,13 ,14 ]and len (deck )>6 :
            return None
        return card_for_cover [0 ]
    else :
        if player_suit ==trump [-2 ]:
            return None
        trumps_for_cover =[bot_card for bot_card in bot_cards if bot_card [-2 ]==trump [-2 ]]
        if trumps_for_cover :
            trumps_for_cover_values =[RUS_CARDS_VALUES [trump_for_cover ]for trump_for_cover in trumps_for_cover ]
            if len (deck )>5 and all ([trump_value in [12 ,13 ,14 ]for trump_value in trumps_for_cover_values ]):
                return None
            trump_for_cover =[bot_card for bot_card in trumps_for_cover
            if RUS_CARDS_VALUES [bot_card ]==min (trumps_for_cover_values )]
            return trump_for_cover [0 ]
        else :
            return None
async def bot_choose_card (state :FSMContext )->Union [str ,None ]:
    states =await state .get_data ()
    bot_cards =states .get ('bot_cards')
    trump =states .get ('trump')
    if not bot_cards :
        return None
    common_cards =[card for card in bot_cards if card [-2 ]!=trump [-2 ]]
    if common_cards :
        common_cards_values =[RUS_CARDS_VALUES [card ]for card in common_cards ]
        result =[card for card in common_cards if RUS_CARDS_VALUES [card ]==min (common_cards_values )]
        return result [0 ]
    trump_cards =[card for card in bot_cards if card [-2 ]==trump [-2 ]]
    trump_cards_values =[RUS_CARDS_VALUES [card ]for card in trump_cards ]
    result =[card for card in trump_cards if RUS_CARDS_VALUES [card ]==min (trump_cards_values )]
    return result [0 ]
async def bot_choose_card_to_add (state :FSMContext )->Union [str ,None ]:
    states =await state .get_data ()
    bot_cards =states .get ('bot_cards')
    if not bot_cards :
        return None
    trump =states .get ('trump')
    desk =states .get ('desk')
    deck =states .get ('deck')
    desk_values =[RUS_CARDS_VALUES [card ]for card in desk ]
    cards_bot_can_add =[bot_card for bot_card in bot_cards if RUS_CARDS_VALUES [bot_card ]in desk_values ]
    if not cards_bot_can_add :
        return None
    common_cards =[card for card in cards_bot_can_add if card [-2 ]!=trump [-2 ]]
    if common_cards :
        if RUS_CARDS_VALUES [common_cards [0 ]]in [13 ,14 ]and len (deck )>0 :
            return None
        return common_cards [0 ]
    all_trumps =[card for card in bot_cards if card [-2 ]==trump [-2 ]]
    if len (all_trumps )==1 and len (deck )>0 and len (bot_cards )>1 :
        return None
    trump_cards =[card for card in cards_bot_can_add if card [-2 ]==trump [-2 ]]
    trump_cards_values =[RUS_CARDS_VALUES [card ]for card in trump_cards ]
    min_trump =[card for card in trump_cards if RUS_CARDS_VALUES [card ]==min (trump_cards_values )][0 ]
    if RUS_CARDS_VALUES [min_trump ]in [11 ,12 ,13 ,14 ]and len (deck )>1 :
        return None
    if RUS_CARDS_VALUES [min_trump ]in [10 ,9 ,8 ,7 ,6 ]and len (all_trumps )<5 :
        return None
    return min_trump
async def player_need_to_cover (message :Message ,state :FSMContext ,bot_card :str )->None :
    states =await state .get_data ()
    cards =states .get ('player_cards')
    trump =states .get ('trump')
    await message .answer ('Чем будете крыть?',
    reply_markup =await player_cover (player_cards =cards ,bot_card =bot_card ,trump =trump ))
async def check_more_cards (state :FSMContext ,check_for :str )->Union [list ,None ]:
    states =await state .get_data ()
    cards_on_desk =states .get ('desk')
    cards =states .get ('player_cards')if check_for =='player'else states .get ('bot_cards')
    values =[RUS_CARDS_VALUES [card ]for card in cards_on_desk ]
    result =[card for card in cards if RUS_CARDS_VALUES [card ]in values ]
    if result :
        return result
    return None
async def bot_try_cover (message :Message ,state :FSMContext ,card :str )->None :
    card_for_cover =await bot_choose_card_for_cover (state ,card )
    if card_for_cover :
        await place_card_on_desk (state ,card_for_cover ,'bot')
        await message .answer (f'🤖 Крою: {card_for_cover }\nЕсть ещё?')
        more_cards =await check_more_cards (state ,'player')
        await sleep (2 )
        if more_cards is not None :
            await message .answer ('Вы можете добавить эти карты',
            reply_markup =await propose_more_cards (cards =more_cards ,action ='cover'))
        else :
            await message .answer ('🤵 Нету...',reply_markup =await show_done_button (action ='next'))
    else :
        await message .answer (f'🤖 {card } беру. Есть ещё?')
        more_cards =await check_more_cards (state ,'player')
        await sleep (2 )
        if more_cards is not None :
            await message .answer ('Вы можете добавить эти карты',
            reply_markup =await propose_more_cards (cards =more_cards ,action ='add'))
        else :
            await message .answer ('🤵 Нету...',reply_markup =await show_done_button (action ='take'))
async def bot_add_all (state :FSMContext )->list [str ]:
    cards =list ()
    card =await bot_choose_card_to_add (state )
    if card :
        await place_card_on_desk (state ,card ,place_for ='bot')
        cards .append (card )
        await bot_add_all (state )
    return cards
async def add_cards_to_player (state :FSMContext )->None :
    states =await state .get_data ()
    player_cards =states .get ('player_cards')
    desk =states .get ('desk')
    player_cards .extend (desk )
    async with state .proxy ()as data :
        data ['player_cards']=player_cards
async def add_cards_to_bot (state :FSMContext )->None :
    states =await state .get_data ()
    bot_cards =states .get ('bot_cards')
    desk =states .get ('desk')
    bot_cards .extend (desk )
    async with state .proxy ()as data :
        data ['bot_cards']=bot_cards
async def bot_turn (message :Message ,state :FSMContext ,target :str )->None :
    await sleep (2 )
    if target =='turn':
        card =await bot_choose_card (state )
    else :
        card =await bot_choose_card_to_add (state )
    if not card :
        async with state .proxy ()as data :
            data ['last_winner']='player'
        await message .answer ('🤖 Ты отбился. Теперь твой черёд.',reply_markup =await show_next_button ())
    else :
        await place_card_on_desk (state ,card ,place_for ='bot')
        await message .answer (card )
        await player_need_to_cover (message ,state ,bot_card =card )
async def bot_full_up (state :FSMContext )->None :
    states =await state .get_data ()
    bot_cards =states .get ('bot_cards')
    if len (bot_cards )<6 :
        new_bot_cards =await hand_out_cards (state ,6 -len (bot_cards ))
        bot_cards .extend (new_bot_cards )
        async with state .proxy ()as data :
            data ['bot_cards']=bot_cards
async def player_full_up (state :FSMContext )->None :
    states =await state .get_data ()
    player_cards =states .get ('player_cards')
    if len (player_cards )<6 :
        new_player_cards =await hand_out_cards (state ,6 -len (player_cards ))
        player_cards .extend (new_player_cards )
        async with state .proxy ()as data :
            data ['player_cards']=player_cards
async def check_winner (state :FSMContext )->bool :
    states =await state .get_data ()
    player_cards ,bot_cards =states .get ('player_cards'),states .get ('bot_cards')
    deck =states .get ('deck')
    trump_used =states .get ('trump_used')
    return len (deck )==0 and trump_used and (len (player_cards )==0 or len (bot_cards )==0 )
async def finish_fool_game (message :Message ,state :FSMContext )->None :
    states =await state .get_data ()
    player_cards ,bot_cards =states .get ('player_cards'),states .get ('bot_cards')
    await sleep (2 )
    if len (player_cards )<len (bot_cards ):
        await message .answer (f'🤵 Вы выиграли!')
        await print_emotion (message ,False )
    elif len (bot_cards )<len (player_cards ):
        await message .answer (f'🤖 Бот выиграл!')
        await print_emotion (message ,True )
    else :
        await message .answer (f'Ничья')
    await state .finish ()
    await sleep (3 )
    commands =await get_default_commands ()
    await message .answer (f"🤖 Во что сыграем?\n\n{commands }",reply_markup =ReplyKeyboardRemove ())
async def play_fool_round (message :Message ,state :FSMContext )->None :
    async with state .proxy ()as data :
        data ['desk']=[]
    await print_fool_desk (message ,state )
    if await check_winner (state ):
        await finish_fool_game (message ,state )
    else :
        states =await state .get_data ()
        if states .get ('last_winner')=='bot':
            await message .answer (f'🤖 Мой ход...')
            await bot_turn (message ,state ,target ='turn')
        else :
            await message .answer (f'🤵 Твой ход...',reply_markup =await fool_player_turn (states .get ('player_cards'),'cover'))