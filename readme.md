# `오덕훈 v0.1` 봇 실행 프로그램

- 이 프로젝트는 [Project_OSSM](https://github.com/Astro-Yu/Project_OSSM) 의  API를 서빙하는 디스코드 봇 `오덕훈 v0.1` 을 실행하는 파이썬 프로그램입니다.
- `오덕훈 v0.1` 은 사용자의 입력을 받아 애니메이션 추천, 랭킹 확인 등의 서비스를 제공합니다.

## 주요 기능

- 애니메이션 추천: 랜덤추천, 퀵추천, 기본추천 기능을 제공합니다. 각 추천 기능은 사용자의 입력을 받아 API를 호출하고, 결과를 디스코드에 보여줍니다.
- 랭킹 확인: 주간랭킹, 월간랭킹을 확인하는 기능을 제공합니다. 랭킹 확인 기능은 API를 호출하고, 결과를 디스코드에 보여줍니다.

## 사용 방법

- 봇 토큰을 환경변수로 설정합니다.
- 파이썬으로 코드를 실행하면 봇이 작동합니다.

## 필요 라이브러리

- discord
- requests
- redis
- json
- dotenv