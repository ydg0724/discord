import discord
from discord.ext import commands
from to import token
import random

bot = commands.Bot(command_prefix="!",intents=discord.Intents.all()) #명령어 실행조건

@bot.event #이벤트 함수 생성, async : 비동기로 실행되는 함수
async def on_ready():   #봇이 시작될 때 실행되는 이벤트함수
    print(f'{bot.user.name} 연결 성공!')
    await bot.change_presence(status=discord.Status.online, activity=None)
    
@bot.command() #command(명령어) 함수 생성
async def hello(message):   #hello를 입력했을 때
    await message.channel.send('Hello, World!')
    
@bot.command()
async def follow(message,arg): #같은말 반복
    await message.send(arg)
    
@bot.command()
async def get_args(message, *args): #인자값들 조인
    await message.send(', '.join(args))
    
@bot.command()
async def 주사위(message):
    await message.send('주사위를 굴립니다.')
    a = random.randint(1,6)
    b = random.randint(1,6)
    texts = discord.Embed(title='주사위 게임 결과')
    texts.add_field(name = message.author.name + '의 숫자', value = ":game_die:"+str(a), inline = True)
    texts.add_field(name = '봇의 숫자',value=":game_die:"+str(b),inline=True)
    if a>b:
        texts.set_footer(text='승리')
        await message.send(embed=texts)
    elif a==b:
        texts.set_footer(text='무승부')
        await message.send(embed=texts)
    elif a<b:
        texts.set_footer(text='패배')
        await message.send(embed=texts)

#@bot.command()
#async def join(message):
    
    
    
@bot.event
async def on_command_error(message,error):  #존재하지 않는 명령어를 입력할 때
    if isinstance(error,commands.CommandNotFound):
        await message.send("명령어를 찾지 못했습니다.")
        
bot.run(token) #to.py에서 가져온 토큰 값
