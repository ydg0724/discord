import discord
import random
import bs4
from discord.ext import commands
from to import token
from youtube_dl import YoutubeDL
from selenium import webdriver
from discord.utils import get
from discord import FFmpegPCMAudio
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

bot = commands.Bot(command_prefix="!",intents=discord.Intents.all(), help_command=None) #명령어 실행조건
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
               

@bot.event #이벤트 함수 생성, async : 비동기로 실행되는 함수
async def on_ready():   #봇이 시작될 때 실행되는 이벤트함수
    print(f'{bot.user.name} 연결 성공!')
    await bot.change_presence(status=discord.Status.online, activity=None) #activity는 상태창

@bot.command()
async def help(ctx):
    await ctx.send(embed = discord.Embed(title="명령어 종류",description= "p or P : 음악을 재생합니다.\nlist : 재생목록을 보여줍니다.\ndel_list n : n번째 재생목록을 제거합니다.\ndel_all : 모든 재생목록을 삭제합니다.",color=0x00ff00))    
    
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
async def shuffle(ctx):
        try:
            global musicnow, user, musictitle,song_queue
            numbershuffle = len(musicnow) - len(user)
            for i in range(numbershuffle):
                shuffle.append(musicnow[0])
                del musicnow[0]
            combine = list(zip(user, musicnow, musictitle, song_queue))
            random.shuffle(combine)
            a, b, c, d = list(zip(*combine))

            user = list(a)
            musicnow = list(b)
            musictitle = list(c)
            song_queue = list(d)

            for i in range(numbershuffle):
                musicnow.insert(0, shuffle[i])

            del shuffle[:]
            await ctx.send("목록이 정상적으로 셔플되었습니다.")
        except:
            await ctx.send("셔플할 목록이 없습니다!")            

@bot.command()
async def restart(ctx):

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if len(user) == 0:
        await ctx.send("등록된 노래가 없습니다.")
    else:
        if len(musicnow) - len(user) >= 1:
            for i in range(len(musicnow) - len(user)):
                del musicnow[0]
        if not vc.is_playing():
            play(ctx)
        else:
            await ctx.send("노래가 이미 재생되고 있습니다.")

#@bot.command()
#async def test(ctx,*,url):
    
            
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
        info_url = []
        
        if not vc.is_playing(): #노래가 재생되고있지 않을 때
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #새로운 방식? 4.0이상 -> 자동으로 chromedriver 경로를 잡아준다.
            driver.get(url) 
            source = driver.page_source
            bs = bs4.BeautifulSoup(source, 'lxml')
            entire = bs.find_all('a',{'id': 'video-title'})
        
            #첫 번째 노래 먼저 실행
            entireNum = entire[0]
            entireText = entireNum.text.strip() #영상제목
            musicurl = entireNum.get('href')
            url = 'https://www.youtube.com'+musicurl
        
    
            musicnow.insert(0, entireText)
            #노래 재생 코드
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            await ctx.send(embed = discord.Embed(title= "노래 재생", description= "현재 "+ musicnow[0] + "을(를) 재생하는 중",color= 0x00ff00))
            
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTION), after = lambda e: play_next(ctx))
        
            i=1
            while(i < len(entire)): #모든 재생목록 불러오기
                name = entire[i].text.strip()   #영상제목
                musicurl = entire[i].get('href')
                urls = 'https://www.youtube.com' + musicurl
                user.append(name)
                musictitle.append(name)
                musicnow.append(name)
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(urls, download=False)
                URL = info['formats'][0]['url']
            
                song_queue.append(URL)
                i = i+1
            await ctx.send(embed = discord.Embed(title = '재생목록 추가'))
        else:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #새로운 방식? 4.0이상 -> 자동으로 chromedriver 경로를 잡아준다.
            driver.get(url) 
            source = driver.page_source
            bs = bs4.BeautifulSoup(source, 'lxml')
            entire = bs.find_all('a',{'id': 'video-title'})
            
            i=0
            while(i < len(entire)): #모든 재생목록 불러오기
                name = entire[i].text.strip()   #영상제목
                musicurl = entire[i].get('href')
                urls = 'https://www.youtube.com' + musicurl
                user.append(name)
                musictitle.append(name)
                musicnow.append(name)
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(urls, download=False)
                URL = info['formats'][0]['url']
            
                song_queue.append(URL)
                i = i+1
        
    elif len(url)>30:   #url로 음악을 찾는 경우
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
            
    
    else:   #유튜브 검색으로 음악을 찾는 경우
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
  
    
@bot.event
async def on_command_error(message,error):  #존재하지 않는 명령어를 입력할 때
    if isinstance(error,commands.CommandNotFound):
        await message.send("명령어를 찾지 못했습니다.")
    
bot.run(token) #to.py에서 가져온 토큰 값
