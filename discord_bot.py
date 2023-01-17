import discord
from discord.ext import commands
from to import token

bot = commands.Bot(command_prefix="!",intents=discord.Intents.all()) #명령어 실행조건

@bot.event #이벤트 함수 생성, async : 비동기로 실행되는 함수
async def on_ready():   #봇이 시작될 때 실행되는 이벤트함수
    print(f'Login bot: {bot.user}')
    
@bot.command() #command 함수 생성
async def hello(message):   #hello를 입력했을 때 실행되는 함수
    await message.channel.send('Hi!')
    
bot.run(token)
