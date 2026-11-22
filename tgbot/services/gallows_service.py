import os
from asyncio import sleep
from random import choice
from aiogram .dispatcher import FSMContext
from aiogram .types import Message ,ReplyKeyboardRemove
from tgbot .services .default_commands import get_default_commands
from tgbot .services .printer import print_gallows_letter ,print_emotion ,print_gallows ,print_correct_word
async def choose_word ()->str :
    path =os .path .abspath (os .path .join ('tgbot','files','words.txt'))
    with open (path ,'r',encoding ='utf8')as file :
        content =file .readlines ()
        return choice (content )
async def get_current_states (state :FSMContext )->tuple [list ,list ,list ,int ]:
    states =await state .get_data ()
    good_letters =states .get ('good_letters')
    bad_letters =states .get ('bad_letters')
    word =states .get ('word')
    errors =states .get ('errors')
    return good_letters ,bad_letters ,word ,errors
async def check_letter (message :Message ,state :FSMContext ,letter :str )->None :
    good_letters ,bad_letters ,word ,errors =await get_current_states (state )
    if letter in good_letters or letter in bad_letters :
        await message .answer ('Ты уже называл эту букву. Введи другую...')
    elif letter in word :
        good_letters .append (letter )
        async with state .proxy ()as data :
            data ['good_letters']=good_letters
    else :
        bad_letters .append (letter )
        errors +=1
        async with state .proxy ()as data :
            data ['bad_letters']=bad_letters
            data ['errors']=errors
        await print_gallows (message ,errors )
    await print_gallows_letter (message ,state )
async def is_word_guessed (good_letters ,word )->bool :
    return all ([letter in good_letters for letter in word ])
async def check_gallows_game_status (message :Message ,state :FSMContext )->None :
    good_letters ,bad_letters ,word ,errors =await get_current_states (state )
    if errors ==8 :
        await finish_gallows_game (message ,state ,'bot')
    elif await is_word_guessed (good_letters ,word ):
        await finish_gallows_game (message ,state ,'player')
    else :
        await message .answer ('Введи букву...')
async def finish_gallows_game (message :Message ,state :FSMContext ,winner :str )->None :
    if winner =='bot':
        await print_correct_word (message ,state )
        await print_emotion (message =message ,bot_win =True )
    else :
        await message .answer ('😎 Вы отгадали слово! Это победа! 🎉🎉🎉')
        await print_emotion (message =message ,bot_win =False )
    await state .finish ()
    commands =await get_default_commands ()
    await sleep (3 )
    await message .answer (f"🤖 Во что сыграем?\n\n{commands }",reply_markup =ReplyKeyboardRemove ())