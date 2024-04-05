import os
from dotenv import load_dotenv, find_dotenv

import redis

# env 설정
dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

rd = redis.StrictRedis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], db=0, password=os.environ["REDIS_PWD"])

"""문자에서 *표를 제거한다."""


def delete_star(word):
    return word.replace('*', '')


"""
실제 실행할 함수
redis의 자동완성을 위한 데이터베이스의 key가 autocomplete2여야 함.

-----------------------
-args-
search_word = 검색할 단어

-return-
Type : list

-----------------------

ex) 
search_word = "오"
return = ["오란고교 호스트부", "오늘부터 신령님", "오버로드"]

"""


def auto_complete(search_word):
    """
    주어진 검색어에 대한 자동완성을 수행합니다.

    Args:
        search_word (str): 자동완성을 위한 검색어입니다.

    Returns:
        list: 검색어와 일치하는 자동완성 제안들의 리스트입니다.
    """
    def mapper(candidates):
        """
        후보 문자열이 검색어로 시작하고 '*'로 끝나는지 확인합니다.

        Args:
            candidates (str): 확인할 후보 문자열입니다.

        Returns:
            bool: 후보 문자열이 검색어로 시작하고 '*'로 끝나면 True이고, 그렇지 않으면 False입니다.
        """
        return candidates.startswith(search_word) and candidates[-1] == "*"

    searchidx = rd.zrank("autocomplete2", search_word)
    result_list = rd.zrange("autocomplete2", start=searchidx, end=searchidx + 1000)
    result_str_list = [member.decode('utf-8') for member in result_list]

    results1 = list(filter(mapper, result_str_list))
    result2 = list(map(delete_star, results1))

    return result2
