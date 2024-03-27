import discord
from discord.ext import commands
import json
import requests

# API 엔드포인트 URL 설정
STANDARD_RECOMMENDATION_URL = "https://jsonplaceholder.typicode.com/posts"
QUICK_RECOMMENDATION_URL = "https://jsonplaceholder.typicode.com/posts"
RANDOM_RECOMMENDATION_URL = "http://121.135.133.7:5000/recommend/random"
headers = {'Content-Type': 'application/json'}

# Discord 봇 객체 생성
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 디스코드 봇 토큰 설정
f = open('token.txt', 'r')
BOT_TOKEN = f.readline()


@bot.event
async def on_ready():  # 봇 실행 시 실행되는 함수
    print(f'{bot.user} 에 로그인하였습니다!')


# TODO : 1. 객체화 해야함
@bot.command(name="test")
async def test(ctx):
    """
    테스트 명령어: 임베드 예시 전송
    """

    # 임베드 객체 생성
    embed1 = discord.Embed(title="애니메이션", description="1번 애니메이션")

    # 필드 추가
    embed1.set_image(
        url="https://image.tving.com/ntgs/contents/CTC/caip/CAIP0900/ko/20200507/P001227842.jpg/dims/resize/F_webp,480")
    embed1.add_field(name="1. 귀멸의 칼날", value="태그 : #액션 #무협 #판타지", inline=False)

    embed2 = discord.Embed(title="애니메이션", description="2번 애니메이션")

    embed2.set_image(
        url="https://image.tving.com/ntgs/contents/CTC/caip/CAIP0900/ko/20161012/P000327935.jpg/dims/resize/F_webp,480")
    embed2.add_field(name="2. 원피스", value="태그 : #모험 #코미디 #소년", inline=False)

    # 봇 채널에 메시지 전송
    await ctx.send("취향에 맞춰 엄선된 애니메이션 2개를 추천합니다.")
    await ctx.send(embed=embed1)
    await ctx.send(embed=embed2)

async def quick(ctx, anime):
    payload = {'input': anime}  # API 요청 시 전달할 데이터

    try:
        response = requests.post(QUICK_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # HTTP 응답 코드가 2xx가 아닌 경우 예외 발생
        result = response.json()
        for i in range(result.__len__()):
            await ctx.send(embed=create_embed(result[i]['title'], image_url = 'https://i.pinimg.com/originals/9f/03/95/9f0395892d90ef261add6c61127cf478.jpg'))
    except requests.exceptions.RequestException as e:
        await ctx.send(f"API 호출 실패: {e}")
def create_embed(title, image_url):
    embed = discord.Embed(title=title, description='???')
    embed.set_image(url=image_url)
    embed.add_field(name="별점",  inline=False)
    return embed


@bot.command()
async def 랜덤추천(ctx):
    # 랜덤 추천은 input 데이터 없음
    payload = {}

    try:
        response = requests.post(RANDOM_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # 2xx 코드가 아닌 경우 예외 발생
        result = response.json()
        print(result)
        for i in range(result.__len__()):
            await ctx.send(embed=create_embed(result[i]['title'], image_url='https://i.pinimg.com/originals/9f/03/95/9f0395892d90ef261add6c61127cf478.jpg'))
    except requests.exceptions.RequestException as e:
        await ctx.send(f"API 호출 실패: {e}")


# 봇 실행

bot.run(BOT_TOKEN)