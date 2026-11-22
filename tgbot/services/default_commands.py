from aiogram import Bot
from aiogram .types import BotCommand ,BotCommandScopeDefault
DEFAULT_COMMANDS =(
('start',"🟢 Запустить бота"),
('craps',"Играть в Craps - покер в кости 🎲"),
('gallows',"Играть в Виселицу 🩸"),
('blackjack',"Играть в Blackjack - 21 очко ♦️♣️"),
('fool','Играть в "Дурака" - классическая карточная игра ♣️♥️️'),
('help',"💡 Вывести справку"),
)
async def set_default_commands (bot :Bot ):
    await bot .set_my_commands (
    commands =[BotCommand (*i )for i in DEFAULT_COMMANDS ],
    scope =BotCommandScopeDefault ()
    )
async def get_default_commands ():
    return '\n'.join ([f'<b>/{command }</b> - {desc }'for command ,desc in DEFAULT_COMMANDS ])