import os
from dotenv import load_dotenv, find_dotenv

import discord
from discord.ext import commands
from discord import app_commands

import json
import requests

from auto_complete import auto_complete

# env 설정
dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

# API 엔드포인트 URL 설정
WAS_ADDRESS = "http://" + os.environ["WAS_HOST"] + ':' + os.environ["WAS_PORT"] + "/recommend/"

STANDARD_RECOMMENDATION_URL = WAS_ADDRESS + "standard"
QUICK_RECOMMENDATION_URL = WAS_ADDRESS + "quick"
RANDOM_RECOMMENDATION_URL = WAS_ADDRESS + "random"

headers = {'Content-Type': 'application/json'}

# Discord 봇 객체 생성
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 디스코드 봇 토큰 설정
BOT_TOKEN = os.environ.get('BOT_TOKEN')


def create_embed(anime_list):
    long_string = "\n".join(anime_list)
    print("create_embed")
    print(long_string)
    embed = discord.Embed(title="이거 추천", description=long_string, color=0x62c1cc)
    return embed


@bot.event
async def on_ready():  # 봇 실행 시 실행되는 함수
    print(f'{bot.user} 에 로그인하였습니다!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


# @bot.command(help="랜덤으로 애니메이션 추천을 받습니다.")
# async def 랜덤추천(ctx):
#     # 랜덤 추천은 input 데이터 없음
#     payload = {}
#
#     try:
#         response = requests.post(RANDOM_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
#         response.raise_for_status()  # 2xx 코드가 아닌 경우 예외 발생
#         titles = [item["title"] for item in response.json()]
#         print(titles)
#         await ctx.send(embed=create_embed(titles))
#     except requests.exceptions.RequestException as e:
#         await ctx.send(f"API 호출 실패: {e}")

@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash command!", ephemeral=True)


@bot.tree.command(name="랜덤추천", description="랜덤으로 애니메이션 추천을 받습니다.")
async def 랜덤추천(interaction: discord.Interaction):
    payload = {}
    try:
        response = requests.post(RANDOM_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # 2xx 코드가 아닌 경우 예외 발생
        titles = [item["title"] for item in response.json()]
        await interaction.response.send_message(embed=create_embed(titles))
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message(f"API 호출 실패: {e}")


@bot.tree.command(name="test", description="test1")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed('안녕'))


class MySelect(discord.ui.Select):
    def __init__(self, anime):
        anime_list = auto_complete(anime)
        print(anime_list)
        options = []
        for i in range(min(5, len(anime_list))):
            anime = anime_list[i]
            option = discord.SelectOption(label=anime, value=anime, description=f"이것은 {anime}에 대한 옵션입니다!")
            options.append(option)
        super().__init__(placeholder="정확한 애니메이션명을 선택해주세요.", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        payload = {'input': self.values[0]}
        print("payload: " + str(payload))
        try:
            response = requests.post(QUICK_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # HTTP 응답 코드가 2xx가 아닌 경우 예외 발생
            titles = [item["title"] for item in response.json()]
            print("api response")
            print(titles)
            await interaction.response.send_message(embed=create_embed(titles))
        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(discord.Embed(title=f"API 호출 실패: {payload}", description=e))


@bot.tree.command(name="퀵추천", description="하나의 애니메이션으로 빠른 추천을 받습니다. 사용법: !퀵추천 [애니메이션 이름]")
async def 퀵추천(interaction: discord.Interaction, anime: str):
    view = discord.ui.View()
    view.add_item(MySelect(anime))
    await interaction.response.send_message("애니메이션 이름을 선택해 주세요!", view=view)


@bot.tree.command(name="select", description="select 만들기")
async def mkselect(interaction: discord.Interaction):
    select = discord.ui.Select(placeholder="셀렉트입니다")
    select.add_option(label="안녕", value=1, description="설명1")
    select.add_option(label="잘가", value=2, description="설명2")
    view = discord.ui.View()
    view.add_item(select)
    async def select_callback(interaction: discord.Interaction):
        await interaction.response.send_message(select.values[0])

    select.callback = select_callback
    await interaction.response.send_message(view=view)




# 봇 실행

bot.run(BOT_TOKEN)
class MyModal():

    input1 = 1
    input2 = 2
    input3 = 3
    input4 = 4
    input5 = 5
    def on_submit(self):
        a = dir(self)
        print(locals())
a = MyModal()
a.on_submit