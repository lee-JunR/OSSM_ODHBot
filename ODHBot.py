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


@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash c제ommand!", ephemeral=True)


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
        self.anime = anime
        options = self._get_options()
        super().__init__(placeholder="후보작들을 꼼꼼히 심사하시고, 당신의 운명을 결정할 최고의 애니메이션을 선택해주세요! 훗훗훗...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        """
        사용자 선택 결과를 기반으로 API를 호출하여 추천 결과를 보여줍니다.

        Args:
            interaction: Discord 상호 작용 객체입니다.
        """
        payload = {'input': self.values[0]}
        print("payload: " + str(payload))
        try:
            response = self._call_api(payload)
            titles = [item["title"] for item in response.json()]
            await interaction.response.send_message(embed=create_embed(titles))
        except Exception as e:  # 모든 예외 처리
            await interaction.response.send_message(discord.Embed(title=f"API 호출 실패: {payload}", description=str(e)))

    def _get_options(self) -> list:
        """
        후보 목록을 생성하여 Select 옵션 목록을 구성합니다.

        Returns:
            Select 옵션 목록입니다.
        """
        anime_candidates = auto_complete(self.anime)
        print(1)
        print(anime_candidates)
        options = []
        for i in range(min(5, len(anime_candidates))):
            anime = anime_candidates[i]
            option = discord.SelectOption(label=anime, value=anime, description=f"이것은 {anime}에 대한 옵션입니다!")
            options.append(option)
        return options

    def _call_api(self, payload: dict) -> requests.Response:
        """
        API 호출을 수행하고 응답을 반환합니다.

        Args:
            payload: API 호출에 필요한 페이로드 딕셔너리입니다.

        Returns:
            API 서버의 응답 객체입니다.
        """
        response = requests.post(QUICK_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # HTTP 응답 코드가 2xx가 아닌 경우 예외 발생
        return response



@bot.tree.command(name="퀵추천", description="하나의 애니메이션으로 빠른 추천을 받습니다. 사용법: !퀵추천 [애니메이션 이름]")
async def 퀵추천(interaction: discord.Interaction, anime: str):
    view = discord.ui.View()
    view.add_item(MySelect(anime))
    await interaction.response.send_message("호오, 애니메이션 이름 선택이라니, 이건 굉장히 중요한 문제인데! 혹시 어떤 애니메이션을 좋아하는지 알려줄 수 있겠니?", view=view)


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
    anime_name_1 = discord.ui.TextInput(label="1번 애니메이션 이름을 알려주게나.", placeholder="애니메이션 이름", style=discord.TextStyle.short)
    anime_name_2 = discord.ui.TextInput(label="2번 애니메이션 이름을 알려주게나.", placeholder="애니메이션 이름", style=discord.TextStyle.short)
    anime_name_3 = discord.ui.TextInput(label="3번 애니메이션 이름을 알려주게나.", placeholder="애니메이션 이름", style=discord.TextStyle.short)
    anime_name_4 = discord.ui.TextInput(label="4번 애니메이션 이름을 알려주게나.", placeholder="애니메이션 이름", style=discord.TextStyle.short)
    anime_name_5 = discord.ui.TextInput(label="5번 애니메이션 이름을 알려주게나.", placeholder="애니메이션 이름", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        """
        사용자 입력 데이터를 추출하고 API를 호출하여 추천 결과를 보여줍니다.

        Args:
            interaction: Discord 상호 작용 객체입니다.
        """
        payload = self._get_payload()
        try:
            response = self._call_api(payload)
            titles = [item["title"] for item in response.json()]
            await interaction.response.send_message(embed=create_embed(titles))
        except Exception as e:  # 모든 예외 처리
            await interaction.response.send_message(discord.Embed(title=f"API 호출 실패: {payload}", description=str(e)))

    def _get_payload(self) -> dict:
        """
        모달에서 입력된 값을 사용하여 API 호출에 필요한 페이로드를 생성합니다.

        Returns:
            API 호출에 필요한 페이로드 딕셔너리입니다.
        """
        return {
            "input1": auto_complete(self.anime_name_1.value)[0],
            "input2": auto_complete(self.anime_name_2.value)[0],
            "input3": auto_complete(self.anime_name_3.value)[0],
            "input4": auto_complete(self.anime_name_4.value)[0],
            "input5": auto_complete(self.anime_name_5.value)[0],
        }

    def _call_api(self, payload: dict) -> requests.Response:
        """
        API 호출을 수행하고 응답을 반환합니다.

        Args:
            payload: API 호출에 필요한 페이로드 딕셔너리입니다.

        Returns:
            API 서버의 응답 객체입니다.
        """
        response = requests.post(STANDARD_RECOMMENDATION_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # HTTP 응답 코드가 2xx가 아닌 경우 예외 발생
        return response

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
