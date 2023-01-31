import discord
import random
import time
import asyncio
import bs4
from discord.ext import commands
from to import token
from youtube_dl import YoutubeDL
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import feedparser

bot = commands.Bot(command_prefix="!",intents=discord.Intents.all()) #명령어 실행조건
client = discord.Client(intents=discord.Intents.all())

user = []       #유저가 입력한 노래 정보
musictitle = [] #가공된 정보의 노래 제목
song_queue = [] #가공된 정보의 노래 링크
musicnow = []   #현재 출력되는 노래 배열


def title(ctx):
    global musictitle
    
    YDL_OPTIONS = {'format' : 'bestaudio','noplaylist':'True'} #youtube_dl 기본설정
    FFMPEG_OPTION = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'} #ffmpeg 기본설정
    
    options = webdriver.ChromeOptions() #크롬 창 안띄우는거? (구현 x)
    options.add_argument("headless")
    
    #검색어의 주소 가져오기
    chromedriver_dir = r"C:\Users\Yang Dong Gyun\Desktop\study\chromedriver_win32\chromedriver.exe"   #chromedriver.exe가 위치한 경로
    #driver = webdriver.Chrome(chromedriver_dir)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #새로운 방식? 4.0이상 -> 자동으로 chromedriver 경로를 잡아준다.
    driver.get("https://www.youtube.com/results?search_query="+ctx+" 가사") 
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a',{'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()
    
    musictitle.append(music)    #노래제목배열 추가
    musicnow.append(music)      #출력 노래배열 추가
    musicurl = entireNum.get('href')
    url = 'https://www.youtube.com'+ musicurl
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']
    driver.quit()
    
    return music,URL

def join(ctx):
    try:
        global vc
        vc = ctx.message.author.voice.channel.connect()
    except:
        try:
            vc.move_to(ctx.message.author.voice.channel)
        except:
            ctx.send("음성채널에 유저가 접속해있지 않습니다.")

def play(ctx):
    global vc
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    URL = song_queue[0]
    del user[0]
    del musictitle[0]
    del song_queue[0]
    vc = get(bot.voice_clients, guild=ctx.guild)
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 
        
def play_next(ctx):
    if len(musicnow) - len(user) >= 2:
        for i in range(len(musicnow) - len(user) - 1):
            del musicnow[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(user) >= 1:
        if not vc.is_playing():
            del musicnow[0]
            URL = song_queue[0]
            del user[0]
            del musictitle[0]
            del song_queue[0]
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
    
    else:
       if not vc.is_playing():
            vc.disconnect()
               
"""def URLPLAY(url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'} 
    
    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url'] 
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        client.loop.create_task(subtitle_song(ctx,URL))        """        

@bot.event #이벤트 함수 생성, async : 비동기로 실행되는 함수
async def on_ready():   #봇이 시작될 때 실행되는 이벤트함수
    print(f'{bot.user.name} 연결 성공!')
    await bot.change_presence(status=discord.Status.online, activity=None) #activity는 상태창
    
@bot.command() #command(명령어) 함수 생성
async def hello(message):   #hello를 입력했을 때
    await message.channel.send('Hello, World!')
    
@bot.command()  #같은말 반복
async def follow(message,arg): 
    await message.send(arg)
    
@bot.command()  #인자값들 조인
async def get_args(message, *args): 
    await message.send(', '.join(args))
    
@bot.command()      #주사위
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

@bot.command()  #채널 접속 코드
async def join(ctx):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:     #다른 채널에 접속해 있는 경우
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("음성채널에 유저가 접속해있지 않습니다.")

    
@bot.command()  #채널 퇴장 코드
async def quit(message):
    try:
        await message.send("봇이 채널에서 나갑니다")
        await vc.disconnect()
    except:
        await message.send("봇이 음성채널에 접속해있지 않습니다")
        
        
@bot.command()
async def test(ctx,*,url):
    try:        #자동입장 코드
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            return
        
    if url.startswith("https://www.youtube.com/playlist?"):
        YDL_OPTIONS = {'format' : 'bestaudio','noplaylist':'True'} #youtube_dl 기본설정
        FFMPEG_OPTION = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'} #ffmpeg 기본설정
        global entireText
        info_url = []
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #새로운 방식? 4.0이상 -> 자동으로 chromedriver 경로를 잡아준다.
        driver.get(url) 
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a',{'id': 'video-title'})
        i=0
        for urls in range(entire[i]):
            print(urls)
            #info_url.append(urls)
            i = i+1
        
        entireNum = entire[0]
        entireText = entireNum.text.strip() #영상제목
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl
        driver.quit()
    
        musicnow.insert(0, entireText)
        #노래 재생 코드
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description= "현재 "+ musicnow[0] + "을(를) 재생하는 중",color= 0x00ff00))
            
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTION), after = lambda e: play_next(ctx))
        
    else:
        user.append(url)
        result, URLTEST = title(url)
        song_queue.append(URLTEST)
        await ctx.send(embed = discord.Embed(title="목록 추가",description=result + "을(를) 목록에 추가했습니다."))
        
@bot.command(aliases = ['P'])
async def p(ctx,*,url):
    try:        #자동입장 코드
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            return
    global entireText
 
    
    if url.startswith("https://www.youtube.com/playlist?"):
        YDL_OPTIONS = {'format' : 'bestaudio','noplaylist':'True'} #youtube_dl 기본설정
        FFMPEG_OPTION = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'} #ffmpeg 기본설정
        
        
        #검색어의 주소 가져오기
        #chromedriver_dir = r"C:\Users\Yang Dong Gyun\Desktop\study\chromedriver_win32\chromedriver.exe"   #chromedriver.exe가 위치한 경로
        #driver = webdriver.Chrome(chromedriver_dir)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #새로운 방식? 4.0이상 -> 자동으로 chromedriver 경로를 잡아준다.
        driver.get(url) 
        source = driver.page_source
            
        #Options = webdriver.ChromeOptions()
        #Options.add_experimental_option("excludeSwitches", ["enable-logging"])
        bs = bs4.BeautifulSoup(source, 'lxml')
        
        entire = bs.find_all('a',{'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip() #영상제목
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl
        driver.quit()
    
            
        musicnow.insert(0, entireText)
        #노래 재생 코드
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description= "현재 "+ musicnow[0] + "을(를) 재생하는 중",color= 0x00ff00))
            
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTION), after = lambda e: play_next(ctx))
        
    #다운로드 받은 플레이 리스트를 리스트에 넣어서 순서대로 실행??
    elif len(url)>30:
        YDL_OPTIONS = {'format' : 'bestaudio', 'noplaylist':'True'} #youtube_dl 기본설정
        FFMPEG_OPTION = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'} #ffmpeg 기본설정
    
        if not vc.is_playing():
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTION))
            
            await ctx.send(embed = discord.Embed(title= "노래 재생", description= "현재 "+url + "을(를) 재생하는 중",color= 0x00ff00))
            
        else:
            user.append(url)
            result, URLTEST = title(url)
            song_queue.append(URL)
            await ctx.send(embed = discord.Embed(title="목록 추가",description=result + "을(를) 목록에 추가했습니다."))
            
    
    else:
        if not vc.is_playing():
            options = webdriver.ChromeOptions() #크롬 창 안띄우는거? (동작 x)
            options.add_argument("headless")
        
            
            YDL_OPTIONS = {'format' : 'bestaudio','noplaylist':'True'}  #youtube_dl 기본설정    
            FFMPEG_OPTION = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}    #ffmpeg 기본설정
            #검색어의 주소 가져오기
            chromedriver_dir = r"C:\Users\Yang Dong Gyun\Desktop\study\chromedriver_win32\chromedriver.exe"   #chromedriver.exe가 위치한 경로
            #driver = webdriver.Chrome(chromedriver_dir)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #새로운 방식? 4.0이상 -> 자동으로 chromedriver 경로를 잡아준다.
            driver.get("https://www.youtube.com/results?search_query="+url+" 가사") 
            source = driver.page_source
            
            #Options = webdriver.ChromeOptions()
            #Options.add_experimental_option("excludeSwitches", ["enable-logging"])
            bs = bs4.BeautifulSoup(source, 'lxml')
            entire = bs.find_all('a',{'id': 'video-title'})
            entireNum = entire[0]
            entireText = entireNum.text.strip() #영상제목
            musicurl = entireNum.get('href')
            url = 'https://www.youtube.com'+musicurl
            driver.quit()
    
            
            musicnow.insert(0, entireText)
            #노래 재생 코드
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            await ctx.send(embed = discord.Embed(title= "노래 재생", description= "현재 "+ musicnow[0] + "을(를) 재생하는 중",color= 0x00ff00))
            
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTION), after = lambda e: play_next(ctx))
            
        else:
            user.append(url)
            result, URLTEST = title(url)
            song_queue.append(URLTEST)
            await ctx.send(embed = discord.Embed(title="목록 추가",description=result + "을(를) 목록에 추가했습니다."))
        
@bot.command()  #URL로 음악재생
async def play_URL(ctx, *, url):
    YDL_OPTIONS = {'format' : 'bestaudio','noplaylist':'True'} #youtube_dl 기본설정
    FFMPEG_OPTION = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'} #ffmpeg 기본설정
    
    if not vc.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTION))
        await ctx.send(embed = discord.Embed(title= "노래 재생", description= "현재 "+url + "을(를) 재생하는 중",color= 0x00ff00))
    else:
        await ctx.send("노래가 이미 재생되고 있습니다!")
        
@bot.command()
async def play_search(ctx,*,msg):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            return
    
    if not vc.is_playing():
        options = webdriver.ChromeOptions() #크롬 창 안띄우는거? (동작 x)
        options.add_argument("headless")
        
        global entireText
        YDL_OPTIONS = {'format' : 'bestaudio','noplaylist':'True'}  #youtube_dl 기본설정    
        FFMPEG_OPTION = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}    #ffmpeg 기본설정
        #검색어의 주소 가져오기
        chromedriver_dir = r"C:\Users\Yang Dong Gyun\Desktop\study\chromedriver_win32\chromedriver.exe"   #chromedriver.exe가 위치한 경로
        #driver = webdriver.Chrome(chromedriver_dir)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #새로운 방식? 4.0이상 -> 자동으로 chromedriver 경로를 잡아준다.
        driver.get("https://www.youtube.com/results?search_query="+msg+" 가사") 
        source = driver.page_source
        #Options = webdriver.ChromeOptions()
        #Options.add_experimental_option("excludeSwitches", ["enable-logging"])
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a',{'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl
        driver.quit()
        
        musicnow.insert(0, entireText)
        #노래 재생 코드
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        await ctx.send(embed = discord.Embed(title= "노래 재생", description= "현재 "+ musicnow[0] + "을(를) 재생하는 중",color= 0x00ff00))
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTION), after = lambda e: play_next(ctx))
    else:
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send(result + "을(를) 목록에 추가했습니다.")

@bot.command()
async def del_all(ctx):
    try:
        ex = len(musicnow) - len(user)
        del user[:]
        del musictitle[:]
        del song_queue[:]
        while True:
            try:
                del musicnow[ex]
            except:
                break
        await ctx.send(embed = discord.Embed(title= "목록 초기화",description="모든 노래 목록이 초기화되었습니다."))
    except:
        await ctx.send(embed = discord.Embed(title= "목록 초기화",description="모든 노래 목록이 초기화되었습니다."))
        
@bot.command() #정지
async def pause(ctx):
    try:
        if vc.is_playing():
            vc.pause()
            await ctx.send(embed = discord.Embed(title= "일시정지" , description= musicnow[0] + "가 일시정지 되었습니다." ))
    except:
        await ctx.send("실행중인 노래가 없습니다.")
        
@bot.command() #다시 재생
async def resume(ctx):
    try: 
        vc.resume()
        await ctx.send(embed = discord.Embed(title = '다시 재생',description=musicnow[0] + "가 재생됩니다."))
    except:
        await ctx.send("정지되어있는 노래가 없습니다.")  

@bot.command() #정지
async def stop(ctx):
    try:
        if vc.is_playing():
            vc.stop()
            await ctx.send(embed = discord.Embed(title = "음악 종료",description= musicnow[0] + "가 종료됩니다."))      
    except:
        await ctx.send("실행중인 노래가 없습니다.")
        
@bot.command()  #목록추가
async def add_list(ctx,*,msg):
    user.append(msg)
    result,URLS = title(msg)
    song_queue.append(URLS)
    await ctx.send(result + "를 대기목록에 추가했습니다.")
    
@bot.command()  #목록삭제
async def del_list(ctx,*,num):
    try:
        adding = len(musicnow) - len(user)
        del user[int(num)-1]
        del musictitle[int(num)-1]
        del song_queue[int(num)-1]
        del musicnow[int(num)-1+adding]
        
        await ctx.send(num+"번째 목록의 노래를 삭제했습니다.")
    except:
        if len(list) == 0:
            await ctx.send("아직 아무 노래도 목록에 추가하지 않았습니다.")
        else:
            if len(list) < int(num):
                await ctx.send("숫자의 범위가 목록개수를 벗어났습니다.")
            else:
                await ctx.send("숫자를 입력해주세요")
                
@bot.command()  #목록 출력
async def list(ctx):
    if len(musictitle) == 0:
        await ctx.send("노래 목록이 없음")
    else:
        global Text
        Text = ""
        for i in range(len(musictitle)):
            Text = Text + '\n' + str(i+1) + '.' + str(musictitle[i])
        
        await ctx.send(embed = discord.Embed(title = "노래목록",description=Text.strip(),color=0x00ff00))
  

#@bot.command()
#async def test(ctx):
   # await ctx.send(ctx)
    
@bot.event
async def on_command_error(message,error):  #존재하지 않는 명령어를 입력할 때
    if isinstance(error,commands.CommandNotFound):
        await message.send("명령어를 찾지 못했습니다.")
    
bot.run(token) #to.py에서 가져온 토큰 값
