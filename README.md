# SJH_Quiz

## 진행 기기 및 소프트웨어 버전

```
Mac

Python 3.12.2

Docker version 28.0.1
```

## 실행 방법
```python
git clone git@github.com:woodstock1993/SJH_Quiz.git

cd SJH_Quiz/

docker compose up -d

docker exec -it fastapi_server /bin/sh

mkdir -p alembic/versions

poetry run alembic revision --autogenerate -m "Initial migration"
poetry run alembic upgrade head

테스트 코드
poetry run pytest tests/test_main.py

Open API
-> http://localhost:8000/docs
```

## 제거 방법
```
docker compose down -v

docker system prune -af 
```

## 기술  
```
Python
FastAPI
PostgreSQL  
SQLAlchemy  
Alembic  
Poetry
Docker
```

## 폴더 구조
```
├── Dockerfile
├── README.md
├── alembic
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── __pycache__
│   ├── api            / FastAPI 엔드포인트(라우트) 정의
│   ├── core           / 애플리케이션 설정 및 토큰
│   ├── crud           / 데이터베이스 CRUD 로직
│   ├── db             / 데이터베이스 연결 및 초기화 관리
│   ├── main.py        / FastAPI 애플리케이션 진입 파일 
│   ├── models         / ORM 모델 정의 
│   ├── schemas        / Pydantic 데이터 검증 스키마
│   └── utils          / 유틸리티 함수 모음
│   └── tests          / 테스트 코드
├── docker-compose.yml
├── poetry.lock        / Poetry 의존성 파일  
├── pyproject.toml     / Poetry 설정 파일
```

## 주요 로직
![Image](https://github.com/user-attachments/assets/8d891f14-2982-4d28-837a-b2373ffac863)

```
1. 퀴즈 시작 시, 사용자별로 생성된 퀴즈 정보를 Redis에 저장합니다.

2. 사용자가 퀴즈 문제에서 선택지를 선택하면, 해당 선택 정보가 Redis에 생성되거나 업데이트됩니다.

3. 사용자가 새로고침하더라도, API는 최초에 받은 문제 정보와 선택한 답안 정보를 함께 반환합니다.

4. 사용자가 퀴즈를 제출하면, 제출된 답안을 채점한 후 사용자에게 제공된 문제 및 선택지 정보를 데이터베이스에 저장합니다.
```

## 테스트 코드

하나의 테스트 코드에 일련의 흐름을 작성하였습니다.

```

1. 관리자 계정 생성 API 테스트

2. 일반 사용자 계정 생성 API 테스트

3. 관리자 토큰 발급 API 테스트

4. 사용자 토큰 발급 API 테스트

5. 퀴즈 생성 API 테스트
   - 퀴즈 1개 생성 시, 문제 100개 및 각 문제당 선택지 5개(총 500개) 자동 생성 로직 검증
   - 각 문제에 최소 2개 이상의 선택지, 최소 1개 이상의 정답 존재 여부 검증
   - 100문제 모두 정답은 1번으로 설정 → 이후 테스트에서 사용자가 1번만 총 20회 선택

6. 사용자 퀴즈 시작 API 테스트
   - 사용자별 퀴즈 응시 정보가 Redis에 저장되는지 검증
   - 각 문제에 대해 사용자가 선택한 답안 정보가 올바르게 저장되는지 확인

7. 퀴즈 새로고침 API 테스트
   - 사용자의 응시 이력 기반으로 퀴즈 문제 및 선택한 답안 상태 불러오기 검증

8. 퀴즈 제출 API 테스트
   - 제출 시 사용자의 응시 정보, 문제, 선택지, 답안이 DB에 저장되는지 확인
   - 사용자가 100문제 중 20문제 정답을 맞힌 결과(score=20) 검증
```

## 테스트 코드 실행 방법
```
pytest tests/test_main.py
```