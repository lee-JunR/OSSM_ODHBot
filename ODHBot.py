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
WAS_ADDRESS = "http://" + os.environ["WAS_HOST"] + ':' + os.environ["WAS_PORT"]

STANDARD_RECOMMENDATION_URL = WAS_ADDRESS + "/recommend/" + "standard"
QUICK_RECOMMENDATION_URL = WAS_ADDRESS + "/recommend/" + "quick"
RANDOM_RECOMMENDATION_URL = WAS_ADDRESS + "/recommend/" + "random"
WEEKLY_RANKING_URL = WAS_ADDRESS + "/rank/weekly"
MONTHLY_RANKING_URL = WAS_ADDRESS + "/rank/monthly"

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
    embed = discord.Embed(title=" 와타시도 애니메이션을 좋아하는 오덕이니까.. 좋은 애니를 추천해주지.", description=long_string, color=0x62c1cc)
    return embed


@bot.event
async def on_ready():  # 봇 실행 시 실행되는 함수
    print(f'{bot.user} 에 로그인하였습니다!')
    try:
        synced = await bot.tree.sync()  # 봇 실행시 활성화된 Slash Command의 개수를 출력해주는 기능
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
        super().__init__(placeholder="후보작들을 꼼꼼히 심사하시고, 당신의 운명을 결정할 최고의 애니메이션을 선택해주세요! 훗훗훗...", min_values=1,
                         max_values=1, options=options)

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
    await interaction.response.send_message("호오, 애니메이션 이름 선택이라니, 이건 굉장히 중요한 문제인데! 혹시 어떤 애니메이션을 좋아하는지 알려줄 수 있겠니?",
                                            view=view)


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


class MyModal(discord.ui.Modal, title="오오, 5개의 애니메이션 이름을 알려준다고?"):
    input1 = (discord.ui.TextInput(label="애니메이션 이름을 알려주게나.", placeholder=f"1번 애니메이션 이름", style=discord.TextStyle.short))
    input2 = (discord.ui.TextInput(label="애니메이션 이름을 알려주게나.", placeholder=f"2번 애니메이션 이름", style=discord.TextStyle.short))
    input3 = (discord.ui.TextInput(label="애니메이션 이름을 알려주게나.", placeholder=f"3번 애니메이션 이름", style=discord.TextStyle.short))
    input4 = (discord.ui.TextInput(label="애니메이션 이름을 알려주게나.", placeholder=f"3번 애니메이션 이름", style=discord.TextStyle.short))
    input5 = (discord.ui.TextInput(label="애니메이션 이름을 알려주게나.", placeholder=f"3번 애니메이션 이름", style=discord.TextStyle.short))

    async def on_submit(self, interaction: discord.Interaction):
        input = []
        input.append(auto_complete(self.input1.value)[0])
        input.append(auto_complete(self.input2.value)[0])
        input.append(auto_complete(self.input3.value)[0])
        input.append(auto_complete(self.input4.value)[0])
        input.append(auto_complete(self.input5.value)[0])

        payload = {'input1': input[0], 'input2': input[1], 'input3': input[2], 'input4': input[3], 'input5': input[4]}
        print("payload: " + str(payload))
        try:
            response = requests.post(STANDARD_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # HTTP 응답 코드가 2xx가 아닌 경우 예외 발생
            titles = [item["title"] for item in response.json()]
            print("api response")
            print(titles)
            await interaction.response.send_message(embed=create_embed(titles))
        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(discord.Embed(title=f"API 호출 실패: {payload}", description=e))

@bot.tree.command(name="기본추천", description="5개의 애니메이션 이름으로 조금 더 취향에 맞는 추천을 받습니다. 사용법: !기본추천")
async def 기본추천(interaction: discord.Interaction):
    await interaction.response.send_modal(MyModal())

@bot.tree.command(name="주간랭킹", description="주간랭킹을 확인하세요!")
async def 주간랭킹(interaction: discord.Interaction):
    # 주간랭킹은 input 데이터 없음
    payload = {}

    try:
        response = requests.get(WEEKLY_RANKING_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # 2xx 코드가 아닌 경우 예외 발생
        result = response.json()
        print(result)
        embed = discord.Embed(title="주간 랭킹", description='주간 랭킹을 확인하세요!', color=discord.Color.random())
        for title, value in result.items():
            embed.add_field(name=title, value="%d회 검색" % value, inline=False)
        await interaction.response.send_message(embed=embed)
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message(f"API 호출 실패: {e}")


@bot.tree.command(name="월간랭킹", description="월간 랭킹을 확인하세요!")
async def 월간랭킹(interaction: discord.Interaction):
    # 월간랭킹은 input 데이터 없음
    payload = {}

    try:
        response = requests.get(MONTHLY_RANKING_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # 2xx 코드가 아닌 경우 예외 발생
        result = response.json()
        print(result)
        embed = discord.Embed(title="월간 랭킹", description='월간 랭킹을 확인하세요!', color=discord.Color.random())
        for title, value in result.items():
            embed.add_field(name=title, value="%d회 검색" % value, inline=False)
        await interaction.response.send_message(embed=embed)
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message(f"API 호출 실패: {e}")


# 봇 실행

bot.run(BOT_TOKEN)
